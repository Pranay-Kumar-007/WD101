from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vector_multidoc import retriever, advanced_rag
import time
import threading
from functools import lru_cache
import hashlib
import warnings
import re
from typing import List, Dict
warnings.filterwarnings("ignore")

# Advanced LLM configuration optimized for accuracy
llm = Ollama(
    model="gemma3:1b",
    temperature=0.15,     # Lower for more consistent reasoning
    num_predict=400,      # More tokens for comprehensive answers
    num_ctx=3072,         # Larger context for advanced RAG
    top_k=30,            # Focused sampling for accuracy
    top_p=0.8,           # Balanced creativity vs accuracy
    repeat_penalty=1.15,  # Better coherence
    num_thread=8,        # More threads for performance
    keep_alive="10m"     # Keep model warm longer
)

parser = StrOutputParser()

# Advanced RAG-optimized prompt template
template = """You are an expert AI assistant with advanced document analysis capabilities. You have access to multiple sources of information retrieved through hybrid search.

Retrieved Context (from multiple search methods):
{context}

Original Question: {question}

Query Analysis: {query_analysis}

Instructions:
- Synthesize information from ALL provided documents
- Cross-reference information between sources when possible
- Indicate confidence level in your answer (High/Medium/Low)
- If information conflicts between sources, mention this
- Cite specific sources when making claims
- If context is insufficient, clearly explain what's missing
- Provide a comprehensive, well-structured answer

Response Format:
Confidence: [High/Medium/Low]
Answer: [Your detailed response]
Sources: [List relevant source documents]

Response:"""

prompt = ChatPromptTemplate.from_template(template)
print("🚀 Advanced RAG-optimized model and prompt loaded")
chain = prompt | llm | parser

# Response caching system
response_cache = {}
max_cache_size = 100

@lru_cache(maxsize=50)
def get_query_hash(question):
    """Generate hash for caching"""
    return hashlib.md5(question.lower().strip().encode()).hexdigest()[:8]

def analyze_query_complexity(question: str) -> Dict:
    """Analyze query complexity and requirements"""
    complexity_indicators = {
        'comparison': any(word in question.lower() for word in ['compare', 'versus', 'vs', 'difference', 'better', 'worse']),
        'analytical': any(word in question.lower() for word in ['analyze', 'explain why', 'how does', 'what causes']),
        'factual': any(word in question.lower() for word in ['what is', 'who is', 'when did', 'where is']),
        'numerical': bool(re.search(r'\d+|how many|how much|percentage|rate', question.lower())),
        'temporal': any(word in question.lower() for word in ['when', 'before', 'after', 'during', 'timeline'])
    }
    
    complexity_score = sum(complexity_indicators.values())
    question_length = len(question.split())
    
    return {
        'complexity_level': 'high' if complexity_score >= 2 or question_length > 15 else 'medium' if complexity_score == 1 or question_length > 8 else 'low',
        'indicators': complexity_indicators,
        'requires_synthesis': complexity_indicators['comparison'] or complexity_indicators['analytical'],
        'word_count': question_length
    }

def format_context_advanced(docs: List, query_analysis: Dict) -> str:
    """Advanced context formatting with hybrid search results"""
    if not docs:
        return "No relevant information found."
    
    context_parts = []
    total_length = 0
    # Adjust max length based on query complexity
    base_length = 3000
    max_length = base_length + (500 if query_analysis.get('complexity_level') == 'high' else 0)
    
    # Group documents by search type and source
    vector_docs = [doc for doc in docs if doc.metadata.get('search_type') == 'vector']
    bm25_docs = [doc for doc in docs if doc.metadata.get('search_type') == 'bm25']
    
    # Process documents with priority to vector search results
    all_docs_prioritized = vector_docs + bm25_docs + [doc for doc in docs if doc not in vector_docs + bm25_docs]
    
    for i, doc in enumerate(all_docs_prioritized[:6], 1):  # Top 6 for comprehensive coverage
        if hasattr(doc, 'page_content'):
            content = doc.page_content.strip()
        elif hasattr(doc, 'text'):
            content = doc.text.strip()
        else:
            content = str(doc).strip()
        
        if content and total_length < max_length:
            # Enhanced source information
            source_info = ""
            search_method = ""
            if hasattr(doc, 'metadata') and doc.metadata:
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', '')
                search_type = doc.metadata.get('search_type', 'standard')
                query_variant = doc.metadata.get('query_variant', '')
                
                search_method = f"[{search_type.upper()}] " if search_type in ['vector', 'bm25'] else ""
                
                if page:
                    source_info = f"{search_method}[Source: {source}, Page: {page}] "
                else:
                    source_info = f"{search_method}[Source: {source}] "
            
            remaining = max_length - total_length
            if len(content) > remaining - len(source_info):
                # Intelligent truncation preserving important information
                truncated = content[:remaining - len(source_info) - 3]
                
                # Try to end at sentence boundary
                sentence_end = max(
                    truncated.rfind('.'),
                    truncated.rfind('!'),
                    truncated.rfind('?')
                )
                
                if sentence_end > len(truncated) * 0.6:  # Keep if we retain 60%+ content
                    content = truncated[:sentence_end + 1]
                else:
                    # Fall back to word boundary
                    word_end = truncated.rfind(' ')
                    if word_end > len(truncated) * 0.8:
                        content = truncated[:word_end] + "..."
                    else:
                        content = truncated + "..."
            
            formatted_content = f"Document {i}: {source_info}{content}"
            context_parts.append(formatted_content)
            total_length += len(formatted_content)
    
    # Add summary of search results
    search_summary = f"\n[Search Summary: Retrieved {len(docs)} documents using hybrid search (Vector: {len(vector_docs)}, BM25: {len(bm25_docs)})]"
    
    return "\n\n".join(context_parts) + search_summary

def process_query_advanced_rag(question):
    """Advanced RAG processing with hybrid search and intelligent analysis"""
    start_time = time.time()
    
    # Enhanced input validation
    question = question.strip()
    if not question:
        return
    
    if len(question) < 3:
        print("⚠️  Question too short. Please provide more details for optimal results.")
        return
    
    # Analyze query complexity
    query_complexity = analyze_query_complexity(question)
    
    # Check cache with similarity scoring
    query_hash = get_query_hash(question)
    if query_hash in response_cache:
        print("⚡ Retrieved from advanced cache:")
        cached_item = response_cache[query_hash]
        if isinstance(cached_item, dict):
            print(cached_item['response'])
            cached_metrics = cached_item['metrics']
            print(f"\n📊 Cached Metrics - Docs: {cached_metrics['docs']}, Quality: {cached_metrics['quality']}")
        else:
            print(cached_item)  # Handle old cache format
        print(f"\n⏱️  Retrieved from cache in {time.time() - start_time:.3f}s")
        return
    
    # Enhanced document retrieval
    print("🔍 Searching for relevant information...", end=" ", flush=True)
    retrieval_start = time.time()
    
    try:
        # Use enhanced retrieval for better accuracy
        docs = retriever.invoke(question)
        
        # Quality check - if we get very few results, try a broader search
        if len(docs) < 3:
            # Extract key terms for broader search
            key_terms = question.lower().split()
            if len(key_terms) > 1:
                broader_query = " ".join(key_terms[:3])  # Use first 3 terms
                additional_docs = retriever.invoke(broader_query)
                # Merge and deduplicate
                all_docs = docs + additional_docs
                seen_content = set()
                docs = []
                for doc in all_docs:
                    content = getattr(doc, 'page_content', str(doc))
                    if content[:100] not in seen_content:
                        docs.append(doc)
                        seen_content.add(content[:100])
        
        retrieval_time = time.time() - retrieval_start
        print(f"Found {len(docs)} relevant documents ({retrieval_time:.2f}s)")
    except Exception as e:
        print(f"\n❌ Retrieval error: {e}")
        return
    
    # Enhanced context formatting
    context = format_context_advanced(docs, query_complexity)
    
    # Quality assessment of retrieved context
    context_quality = "High" if len(docs) >= 3 and len(context) > 500 else "Medium" if len(docs) >= 2 else "Low"
    
    # Generate response with enhanced streaming
    print(f"🤖 Generating accurate response (Context quality: {context_quality})...")
    generation_start = time.time()
    
    response_parts = []
    # Get structured query analysis for prompt
    query_analysis_text = f"Complexity: {query_complexity['complexity_level']}, Type: {', '.join([k for k, v in query_complexity['indicators'].items() if v])}"
    
    try:
        for chunk in chain.stream({
            "question": question,
            "context": context,
            "query_analysis": query_analysis_text
        }):
            print(chunk, end="", flush=True)
            response_parts.append(chunk)
    except Exception as e:
        print(f"\n❌ Generation error: {e}")
        return
    
    full_response = "".join(response_parts)
    generation_time = time.time() - generation_start
    total_time = time.time() - start_time
    
    # Advanced caching with metadata
    response_quality_score = len(full_response.strip())
    if response_quality_score > 30:  # Cache substantial responses
        if len(response_cache) >= max_cache_size:
            # Remove oldest entries
            oldest_keys = list(response_cache.keys())[:15]
            for key in oldest_keys:
                del response_cache[key]
        
        response_cache[query_hash] = {
            'response': full_response,
            'metrics': {
                'docs': len(docs),
                'quality': context_quality,
                'complexity': query_complexity['complexity_level']
            }
        }
    
    # Comprehensive metrics reporting
    print(f"\n\n📊 ADVANCED RAG METRICS:")
    print(f"⏱️  Total time: {total_time:.2f}s (Retrieval: {retrieval_time:.2f}s, Generation: {generation_time:.2f}s)")
    
    # Calculate vector vs BM25 distribution
    vector_count = len([d for d in docs if d.metadata.get('search_type') == 'vector'])
    bm25_count = len([d for d in docs if d.metadata.get('search_type') == 'bm25'])
    
    print(f"🔍 Search results: {len(docs)} docs ({vector_count} vector + {bm25_count} BM25)")
    print(f"🧠 Query complexity: {query_complexity['complexity_level']} ({query_complexity['word_count']} words)")
    print(f"📄 Context size: {len(context):,} characters")
    print(f"🎯 Context quality: {context_quality}")
    print(f"📝 Response length: {len(full_response)} characters")
    if query_complexity['requires_synthesis']:
        print(f"🔗 Synthesis required: Multi-document analysis performed")
    print("-" * 75)

# Performance monitoring
query_count = 0
total_response_time = 0
start_session = time.time()

print("\n" + "="*70)
print("🚀 ADVANCED RAG SYSTEM WITH HYBRID SEARCH READY")
print("="*70)
print("🎆 Features: Hybrid Search | Query Rewriting | LLM Reranking | Offline")
print("Commands:")
print("  • Type 'quit', 'exit', or 'q' to stop")
print("  • Type 'stats' for performance statistics")
print("  • Type 'cache' to see cached queries")
print("  • Type 'clear' to clear cache")
print("-" * 60)

while True:
    try:
        question = input("\n❓ Your question: ").strip()
        
        # Handle commands
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if question.lower() == 'stats':
            session_time = time.time() - start_session
            if query_count > 0:
                avg_time = total_response_time / query_count
                print(f"📊 Advanced RAG System Stats:")
                print(f"   • Queries processed: {query_count}")
                print(f"   • Average response time: {avg_time:.2f}s")
                print(f"   • Session duration: {session_time:.1f}s")
                print(f"   • Cached responses: {len(response_cache)}")
                print(f"   • Queries per minute: {(query_count/session_time*60):.1f}")
                print(f"   • Vector index: {getattr(advanced_rag.vectorstore, 'index', {}).get('ntotal', 'N/A')} embeddings")
                print(f"   • BM25 index: {'Active' if advanced_rag.bm25_retriever else 'Inactive'}")
            else:
                print("📊 No queries processed yet")
            continue
        
        if question.lower() == 'cache':
            if response_cache:
                print(f"💾 Cached queries ({len(response_cache)}):") 
                for i, key in enumerate(list(response_cache.keys())[-5:], 1):
                    print(f"   {i}. {key}")
            else:
                print("💾 No cached queries")
            continue
        
        if question.lower() == 'clear':
            response_cache.clear()
            print("🗑️  Cache cleared")
            continue
        
        if not question:
            print("Please enter a question or command")
            continue
        
        # Process query with advanced RAG techniques
        query_start = time.time()
        process_query_advanced_rag(question)
        
        query_time = time.time() - query_start
        query_count += 1
        total_response_time += query_time
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
        break
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please try again")

# Session summary
print("\n" + "="*60)
print("📊 SESSION SUMMARY")
print("="*60)
if query_count > 0:
    session_time = time.time() - start_session
    avg_time = total_response_time / query_count
    print(f"Queries processed: {query_count}")
    print(f"Total session time: {session_time:.1f}s")
    print(f"Average response time: {avg_time:.2f}s")
    print(f"Cached responses: {len(response_cache)}")
    print(f"Performance: {(query_count/session_time*60):.1f} queries/min")
else:
    print("No queries processed")
print("\n👋 Thanks for using the optimized Q&A system!")