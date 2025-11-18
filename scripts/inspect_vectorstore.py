#!/usr/bin/env python3
"""Chroma 벡터 스토어 데이터 확인 스크립트"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()


def inspect_vectorstore(persist_directory: str = "data/vectorstore"):
    """벡터 스토어 내용 확인"""

    print("="*60)
    print("  Chroma 벡터 스토어 데이터 확인")
    print("="*60)

    if not os.path.exists(persist_directory):
        print(f"\n❌ 벡터 스토어를 찾을 수 없습니다: {persist_directory}")
        print("\n먼저 벡터 스토어를 구축하세요:")
        print("  python scripts/build_vectorstore.py")
        sys.exit(1)

    print(f"\n📂 벡터 스토어 경로: {os.path.abspath(persist_directory)}")

    # Ollama 임베딩 모델 로드
    embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-m3-korean")
    embeddings = OllamaEmbeddings(model=embedding_model)

    # 벡터 스토어 로드
    print(f"\n🔄 벡터 스토어 로드 중...")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="faq_collection"
    )

    # 컬렉션 정보 가져오기
    collection = vectorstore._collection

    print("\n" + "="*60)
    print("📊 벡터 스토어 통계")
    print("="*60)
    print(f"총 문서 수: {collection.count()}")

    # 전체 데이터 조회 (최대 100개)
    results = collection.get(
        include=['metadatas', 'documents'],
        limit=100
    )

    print(f"\n📋 저장된 문서 목록 (최대 100개):")
    print("-"*60)

    if results['ids']:
        for i, (doc_id, metadata, document) in enumerate(zip(
            results['ids'],
            results['metadatas'],
            results['documents']
        ), 1):
            print(f"\n[{i}] ID: {doc_id}")
            print(f"    제목: {metadata.get('title', 'N/A')}")
            print(f"    카테고리: {metadata.get('category', 'N/A')}")
            print(f"    태그: {metadata.get('tags', 'N/A')}")
            print(f"    도움됨: {metadata.get('helpful_count', 0)}회")
            print(f"    생성일: {metadata.get('created_at', 'N/A')}")
            print(f"    문서 길이: {len(document)}자")
            # 문서 미리보기
            preview = document.replace('\n', ' ')[:150]
            print(f"    내용 미리보기: {preview}...")
    else:
        print("저장된 문서가 없습니다.")

    # 카테고리별 통계
    print("\n" + "="*60)
    print("📊 카테고리별 통계")
    print("="*60)

    categories = {}
    for metadata in results['metadatas']:
        category = metadata.get('category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1

    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}개")

    # 샘플 검색 테스트
    print("\n" + "="*60)
    print("🔍 샘플 검색 테스트")
    print("="*60)

    test_queries = [
        "알림이 안와요",
        "비밀번호 찾기",
    ]

    for query in test_queries:
        print(f"\n📌 쿼리: '{query}'")
        results = vectorstore.similarity_search_with_score(query, k=3)

        for i, (doc, score) in enumerate(results, 1):
            print(f"  [{i}] 유사도: {score:.4f}")
            print(f"      제목: {doc.metadata['title']}")
            print(f"      카테고리: {doc.metadata['category']}")

    print("\n" + "="*60)
    print("✅ 확인 완료!")
    print("="*60)


if __name__ == "__main__":
    inspect_vectorstore()
