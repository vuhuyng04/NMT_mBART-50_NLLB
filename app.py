from flask import Flask, render_template, request, jsonify
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import os
import time

app = Flask(__name__)

# Set up mbart50 translation model
mbart_model_name = "nguyenvuhuy/en-vi-mbart50_TMG301"
# token = "###"

mbart_tokenizer = AutoTokenizer.from_pretrained(mbart_model_name, use_auth_token=token)
mbart_model = AutoModelForSeq2SeqLM.from_pretrained(mbart_model_name, use_auth_token=token)
mbart_translator = pipeline("translation", model=mbart_model, tokenizer=mbart_tokenizer)

# Set up nllb-200 translation model
nllb_model_name = "nguyenvuhuy/en-vi-nllb-200_TMG301"
nllb_tokenizer = AutoTokenizer.from_pretrained(nllb_model_name, use_auth_token=token)
nllb_model = AutoModelForSeq2SeqLM.from_pretrained(nllb_model_name, use_auth_token=token)
nllb_translator = pipeline("translation", model=nllb_model, tokenizer=nllb_tokenizer)

# Language codes for NLLB model
nllb_lang_codes = {"en": "eng_Latn", "vi": "vie_Latn"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '').strip()
    direction = data.get('direction', 'en_to_vi')
    
    if not text.strip():
        return jsonify({'error': 'No text provided'})
    
    result = {
        'source_text': text,
        'mbart': {},
        'nllb': {}
    }
    
    try:
        # Configure language settings
        if direction == 'en_to_vi':
            mbart_src_lang, mbart_tgt_lang = "en_XX", "vi_VN"
            nllb_src_lang, nllb_tgt_lang = nllb_lang_codes["en"], nllb_lang_codes["vi"]
        else:
            mbart_src_lang, mbart_tgt_lang = "vi_VN", "en_XX"
            nllb_src_lang, nllb_tgt_lang = nllb_lang_codes["vi"], nllb_lang_codes["en"]
        
        # Translate with mbart model
        mbart_start_time = time.time()
        mbart_translated = mbart_translator(text, src_lang=mbart_src_lang, tgt_lang=mbart_tgt_lang)
        mbart_time = time.time() - mbart_start_time
        
        # Translate with nllb model
        nllb_start_time = time.time()
        nllb_translated = nllb_translator(text, src_lang=nllb_src_lang, tgt_lang=nllb_tgt_lang)
        nllb_time = time.time() - nllb_start_time
        
        # Prepare result
        result['mbart'] = {
            'translation': mbart_translated[0]['translation_text'],
            'time': round(mbart_time, 3)
        }
        
        result['nllb'] = {
            'translation': nllb_translated[0]['translation_text'],
            'time': round(nllb_time, 3)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)