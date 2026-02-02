# final_presentation.py - 100% WORKING FOR PRESENTATION
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from datetime import datetime, timedelta

PORT = 8888  # Port yang jarang digunakan

print("="*70)
print("🎯 FINAL PRESENTATION SYSTEM - SRS MODEL")
print("="*70)

# Simple Database
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.setup()
    
    def setup(self):
        c = self.conn.cursor()
        c.execute('CREATE TABLE words (id INTEGER PRIMARY KEY, english TEXT, indonesian TEXT)')
        c.execute('CREATE TABLE reviews (word_id INTEGER, score INTEGER, next_date TEXT)')
        
        # Add sample data
        words = [
            (1, 'algorithm', 'algoritma'),
            (2, 'database', 'basis data'),
            (3, 'function', 'fungsi'),
            (4, 'variable', 'variabel'),
            (5, 'software', 'perangkat lunak')
        ]
        c.executemany('INSERT INTO words VALUES (?,?,?)', words)
        self.conn.commit()
        print(f"✅ Database ready with {len(words)} words")
    
    def get_stats(self):
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*) FROM words')
        total = c.fetchone()[0]
        
        c.execute('SELECT COUNT(DISTINCT word_id) FROM reviews')
        reviewed = c.fetchone()[0]
        
        c.execute('SELECT AVG(score) FROM reviews')
        avg_score = c.fetchone()[0] or 0
        
        return {
            'status': 'success',
            'data': {
                'total_words': total,
                'reviewed_words': reviewed,
                'avg_score': round(float(avg_score), 2),
                'progress': f'{reviewed}/{total} ({reviewed/max(total,1)*100:.0f}%)'
            }
        }
    
    def get_words(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM words')
        rows = c.fetchall()
        return {
            'status': 'success',
            'data': [{'id': r[0], 'english': r[1], 'indonesian': r[2]} for r in rows]
        }
    
    def add_review(self, word_id, score):
        intervals = {1:1, 2:1, 3:2, 4:4, 5:7}
        interval = intervals.get(score, 1)
        next_date = (datetime.now() + timedelta(days=interval)).strftime('%Y-%m-%d')
        
        c = self.conn.cursor()
        c.execute('INSERT INTO reviews (word_id, score, next_date) VALUES (?,?,?)',
                 (word_id, score, next_date))
        self.conn.commit()
        
        return {
            'status': 'success',
            'message': f'Review saved. Next review in {interval} days ({next_date})',
            'data': {'interval': interval, 'next_review': next_date}
        }

# Initialize database
db = Database()

# HTTP Handler
class SRSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] GET {self.path}")
        
        if self.path == '/':
            self.serve_frontend()
        
        elif self.path == '/api/stats':
            self.send_json(db.get_stats())
        
        elif self.path == '/api/words':
            self.send_json(db.get_words())
        
        elif self.path == '/api/ping':
            self.send_json({'status': 'ok', 'message': 'API is working!'})
        
        else:
            self.send_error(404, f"Not found: {self.path}")
    
    def do_POST(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] POST {self.path}")
        
        if self.path == '/api/review':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                word_id = data.get('word_id')
                score = data.get('score')
                
                if not word_id or not score:
                    self.send_json({'status': 'error', 'message': 'Missing parameters'}, 400)
                    return
                
                result = db.add_review(int(word_id), int(score))
                self.send_json(result)
                
            except Exception as e:
                self.send_json({'status': 'error', 'message': str(e)}, 500)
        
        else:
            self.send_error(404, f"Not found: {self.path}")
    
    def serve_frontend(self):
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SRS Model - Presentasi Informatika</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #f0f0f0;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #7f8c8d;
            font-size: 1.2em;
        }
        .section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
            border-left: 5px solid #3498db;
        }
        .api-test {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #e0e0e0;
        }
        .btn {
            background: #3498db;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin: 10px 5px;
            font-size: 16px;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        .response-box {
            background: #2d2d2d;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-family: monospace;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }
        .success { border-left-color: #2ecc71; }
        .error { border-left-color: #e74c3c; }
        .architecture {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 30px 0;
        }
        .layer {
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .layer h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔤 MODEL INFORMATIKA: SISTEM SPACED REPETITION</h1>
            <div class="subtitle">Tugas Akhir Informatika - Implementasi Lengkap Frontend, Backend, Database</div>
        </div>
        
        <!-- ARCHITECTURE -->
        <div class="section">
            <h2>🏗️ ARSITEKTUR SISTEM TERINTEGRASI</h2>
            <div class="architecture">
                <div class="layer">
                    <h3>🎨 FRONTEND</h3>
                    <p>HTML/CSS/JavaScript</p>
                    <p>User Interface</p>
                    <p>API Calls</p>
                </div>
                <div class="layer">
                    <h3>⚙️ BACKEND</h3>
                    <p>Python HTTP Server</p>
                    <p>API Endpoints</p>
                    <p>Business Logic</p>
                </div>
                <div class="layer">
                    <h3>💾 DATABASE</h3>
                    <p>SQLite In-Memory</p>
                    <p>CRUD Operations</p>
                    <p>Data Persistence</p>
                </div>
            </div>
        </div>
        
        <!-- API TESTING -->
        <div class="section">
            <h2>🔗 TEST INTEGRASI API</h2>
            
            <div class="api-test">
                <h3>✅ Test 1: Ping API (GET /api/ping)</h3>
                <button class="btn" onclick="testApi('ping')">Test Connection</button>
                <div class="response-box" id="result-ping">Click button to test</div>
            </div>
            
            <div class="api-test">
                <h3>📊 Test 2: Get Statistics (GET /api/stats)</h3>
                <button class="btn" onclick="testApi('stats')">Get Stats</button>
                <div class="response-box" id="result-stats">Click button to test</div>
            </div>
            
            <div class="api-test">
                <h3>📚 Test 3: Get Vocabulary (GET /api/words)</h3>
                <button class="btn" onclick="testApi('words')">Get Words</button>
                <div class="response-box" id="result-words">Click button to test</div>
            </div>
            
            <div class="api-test success">
                <h3>🎯 Test 4: Submit Review (POST /api/review)</h3>
                <p>Simulasi algoritma SRS: skor menentukan interval review</p>
                <select id="word-select">
                    <option value="1">algorithm</option>
                    <option value="2">database</option>
                    <option value="3">function</option>
                </select>
                <select id="score-select">
                    <option value="1">1 - Very Hard (1 day)</option>
                    <option value="2">2 - Hard (1 day)</option>
                    <option value="3">3 - Moderate (2 days)</option>
                    <option value="4">4 - Easy (4 days)</option>
                    <option value="5">5 - Very Easy (7 days)</option>
                </select>
                <button class="btn" onclick="testPostReview()">Submit Review</button>
                <div class="response-box" id="result-review">Submit a review to test</div>
            </div>
        </div>
        
        <!-- ALGORITHM EXPLANATION -->
        <div class="section">
            <h2>🔢 ALGORITMA SPACED REPETITION</h2>
            <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                <tr style="background:#3498db; color:white;">
                    <th style="padding:15px; text-align:left;">Skor User</th>
                    <th style="padding:15px; text-align:left;">Keterangan</th>
                    <th style="padding:15px; text-align:left;">Interval (hari)</th>
                    <th style="padding:15px; text-align:left;">Prinsip</th>
                </tr>
                <tr style="background:#f8f9fa;">
                    <td style="padding:12px; border-bottom:1px solid #ddd;">1-2</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">Sulit diingat</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">1</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">Review cepat</td>
                </tr>
                <tr>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">3</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">Cukup</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">2</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">Sedikit meningkatkan</td>
                </tr>
                <tr style="background:#f8f9fa;">
                    <td style="padding:12px; border-bottom:1px solid #ddd;">4-5</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">Mudah diingat</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">4-7</td>
                    <td style="padding:12px; border-bottom:1px solid #ddd;">Interval panjang</td>
                </tr>
            </table>
            <p><strong>Contoh:</strong> User memberi skor 4 untuk kata "algorithm" → Sistem akan mengingatkan review dalam 4 hari.</p>
        </div>
        
        <!-- PRESENTATION INFO -->
        <div class="section">
            <h2>🎓 UNTUK PRESENTASI TUGAS AKHIR</h2>
            <p><strong>Model Informatika ini terdiri dari:</strong></p>
            <ol>
                <li><strong>Model Data:</strong> Struktur database SQLite untuk menyimpan kosakata dan riwayat belajar</li>
                <li><strong>Model Algoritma:</strong> Fungsi komputasi f(score) = interval berdasarkan teori Spaced Repetition</li>
                <li><strong>Model Simulasi:</strong> Web interface untuk mensimulasikan proses belajar dengan feedback loop</li>
            </ol>
            <p><strong>Relevansi dengan KTI:</strong> Implementasi prinsip SRS yang digunakan Duolingo untuk optimasi pembelajaran kosakata.</p>
        </div>
    </div>
    
    <script>
        async function testApi(endpoint) {
            try {
                const response = await fetch(`/api/${endpoint}`);
                const data = await response.json();
                document.getElementById(`result-${endpoint}`).textContent = 
                    JSON.stringify(data, null, 2);
                    
                // Update UI color based on status
                const box = document.getElementById(`result-${endpoint}`).parentElement;
                box.className = data.status === 'error' ? 'api-test error' : 'api-test success';
                
            } catch (error) {
                document.getElementById(`result-${endpoint}`).textContent = 
                    `Error: ${error.message}`;
                document.getElementById(`result-${endpoint}`).parentElement.className = 'api-test error';
            }
        }
        
        async function testPostReview() {
            const wordId = document.getElementById('word-select').value;
            const score = document.getElementById('score-select').value;
            
            try {
                const response = await fetch('/api/review', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({word_id: parseInt(wordId), score: parseInt(score)})
                });
                const data = await response.json();
                document.getElementById('result-review').textContent = 
                    JSON.stringify(data, null, 2);
                    
                // Refresh stats after review
                setTimeout(() => testApi('stats'), 500);
                
            } catch (error) {
                document.getElementById('result-review').textContent = 
                    `Error: ${error.message}`;
            }
        }
        
        // Test API connection on load
        window.onload = () => {
            testApi('ping');
            console.log('SRS System ready for presentation!');
        };
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def log_message(self, format, *args):
        # Custom logging
        pass

# Run server
def main():
    print(f"📡 Starting presentation server on port {PORT}")
    print(f"🌐 Open browser to: http://localhost:{PORT}")
    print("="*70)
    print("🎮 DEMO INSTRUCTIONS:")
    print("1. Open the URL in browser")
    print("2. Click API test buttons")
    print("3. Verify all layers are connected")
    print("="*70)
    
    server = HTTPServer(('', PORT), SRSHandler)
    
    try:
        print("✅ Server started successfully!")
        print("⚡ Press Ctrl+C to stop")
        print("="*70)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Presentation complete. Server stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()