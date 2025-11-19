"""Search Knowledge Node - RAG 검색

Chroma 벡터 스토어에서 관련 FAQ를 검색합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
from typing import Dict, Any

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

from src.models.state import SupportState

# 환경 변수 로드
load_dotenv()


def search_knowledge_node(state: SupportState) -> Dict[str, Any]:
    """
    RAG 검색 노드
    - 벡터 스토어에서 관련 FAQ 검색
    - 유사도 점수 계산

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (retrieved_docs, relevance_score 포함)
    """

    # 벡터 스토어 로드
    embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-m3-korean")
    embeddings = OllamaEmbeddings(
        model=embedding_model,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

    vectorstore = Chroma(
        persist_directory=os.getenv("VECTORSTORE_PATH", "data/vectorstore"),
        embedding_function=embeddings,
        collection_name="faq_collection"
    )

    # 유사 문서 검색 (상위 3개)
    query = state["current_query"]
    docs_with_scores = vectorstore.similarity_search_with_score(
        query,
        k=3
    )

    # 검색 결과 저장
    retrieved_docs = []
    threshold = 0.9  # 임계값 (0.82~0.86 정도의 점수가 나와서 0.9로 상향 조정)

    for doc, score in docs_with_scores:
        if score <= threshold:
            retrieved_docs.append({
                "id": doc.metadata.get("id", ""),
                "category": doc.metadata.get("category", ""),
                "title": doc.metadata.get("title", ""),
                "content": doc.page_content,
                "tags": doc.metadata.get("tags", []),
                "score": float(score),
                "source": doc.metadata.get("source", "faq"),
                "helpful_count": doc.metadata.get("helpful_count", 0)
            })

    state["retrieved_docs"] = retrieved_docs

    # 최고 점수 저장 (낮을수록 좋음 - 코사인 거리)
    state["relevance_score"] = docs_with_scores[0][1] if docs_with_scores else 1.0
    state["status"] = "planning"

    return state
