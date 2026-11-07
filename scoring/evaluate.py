"""Illustrative practice scores only, not validated assessment of employability."""
import re
from .embeddings import encode
from .similarity import best_similarity

def chunks(text, max_words=45):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    result, current = [], []
    for sentence in sentences:
        for word in sentence.split():
            current.append(word)
            if len(current) >= max_words:
                result.append(' '.join(current)); current = []
    if current: result.append(' '.join(current))
    return result

def evaluate(transcript, rubric):
    if not transcript.strip():
        return {'score':None,'criteria':[],'feedback':['No clear speech was transcribed. Try recording again or correct the transcript.'],'status':'insufficient_audio'}
    parts = chunks(transcript)
    results=[]
    for criterion in rubric['criteria']:
        sim=best_similarity(parts, criterion['references'], encode)
        # Demo mapping only. Calibrate using human-rated examples before real deployment.
        coverage=max(0.0,min(1.0,(sim-0.20)/0.50))
        points=round(criterion['weight']*coverage)
        results.append({'id':criterion['id'],'label':criterion['label'],'points':points,'max_points':criterion['weight'],'similarity':round(sim,3),'tip':criterion['tip']})
    return {'score':sum(x['points'] for x in results),'criteria':results,'feedback':[x['tip'] for x in sorted(results,key=lambda r:r['points']/r['max_points'])[:2]],'status':'experimental'}
