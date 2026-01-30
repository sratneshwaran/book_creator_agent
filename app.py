from flask import Flask, render_template, request, Response, session, send_file
from book_agent import BookGenerator
import json
import io
import time
from html import escape

try:
    import markdown
except ImportError:
    markdown = None

app = Flask(__name__)
app.config.from_object('config.Config')

# In-memory storage for the generated file (for simplicity in this demo)
# In production, use a database or file system with session IDs.
generated_books = {"rtf": None, "html": None}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form.get('topic')
    
    def generate_stream():
        writer = BookGenerator()
        full_manuscript = ""
        
        # 1. Generate Outline
        yield f"data: {json.dumps({'status': 'thinking', 'message': 'Consulting the muse... Generating topic list...'})}\n\n"
        chapters = writer.generate_outline(topic)
        yield f"data: {json.dumps({'status': 'thinking', 'message': f'Outline generated: {len(chapters)} chapters identified.'})}\n\n"
        
        # 2. Loop through chapters
        raw_text_storage = []
        for i, chapter in enumerate(chapters):
            yield f"data: {json.dumps({'status': 'thinking', 'message': f'Writing {chapter} ({i+1}/{len(chapters)})...'})}\n\n"
            
            chapter_content = writer.write_chapter(chapter, topic)
            
            # Append to raw text for the final prompt
            chapter_section = f"\n\n## {chapter}\n\n{chapter_content.strip()}\n"
            raw_text_storage.append(chapter_section)
            
            # Stream the draft content to the UI immediately
            yield f"data: {json.dumps({'status': 'draft', 'content': chapter_section})}\n\n"

        full_draft = "".join(raw_text_storage)

        # 3. Proofread and RTF Conversion
        yield f"data: {json.dumps({'status': 'thinking', 'message': 'Proofreading and formatting to RTF...'})}\n\n"
        rtf_content = writer.proofread_and_format_rtf(full_draft)

        # Create HTML from markdown/plaintext draft
        if markdown:
            html_content = markdown.markdown(full_draft, extensions=["extra"])
        else:
            # Fallback simple escape to avoid dependency issues
            html_content = f"<pre>{escape(full_draft)}</pre>"

        # Store for download
        generated_books['rtf'] = rtf_content
        generated_books['html'] = html_content
        
        # Final Completion Signal
        yield f"data: {json.dumps({'status': 'complete', 'message': 'Book generation complete!'})}\n\n"

    return Response(generate_stream(), mimetype='text/event-stream')

@app.route('/download/<fmt>')
def download(fmt):
    if fmt == 'rtf':
        rtf_data = generated_books.get('rtf')
        if not rtf_data:
            return "No book generated yet", 404

        clean_rtf = rtf_data.replace("```rtf", "").replace("```", "").strip()
        mem_file = io.BytesIO()
        mem_file.write(clean_rtf.encode('utf-8'))
        mem_file.seek(0)

        return send_file(
            mem_file,
            as_attachment=True,
            download_name='generated_book.rtf',
            mimetype='application/rtf'
        )

    if fmt == 'html':
        html_data = generated_books.get('html')
        if not html_data:
            return "No book generated yet", 404

        mem_file = io.BytesIO()
        mem_file.write(html_data.encode('utf-8'))
        mem_file.seek(0)

        return send_file(
            mem_file,
            as_attachment=True,
            download_name='generated_book.html',
            mimetype='text/html'
        )

    return "Unsupported format", 400

# Backward compatibility for existing links
@app.route('/download')
def download_default():
    return download('rtf')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    