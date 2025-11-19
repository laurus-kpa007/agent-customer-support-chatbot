#!/usr/bin/env python3
"""벡터 스토어 검색 테스트"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()

def test_vectorstore_search():
    """벡터 스토어 검색 테스트"""

    print("=" * 60)
    print("  벡터 스토어 검색 테스트")
    print("=" * 60)

    # 벡터 스토어 로드
    print("\n1. 벡터 스토어 로드 중...")
    embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-m3-korean")
    print(f"   - 임베딩 모델: {embedding_model}")

    try:
        embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        print("   ✅ 임베딩 모델 로드 성공")
    except Exception as e:
        print(f"   ❌ 임베딩 모델 로드 실패: {e}")
        return

    try:
        vectorstore = Chroma(
            persist_directory=os.getenv("VECTORSTORE_PATH", "data/vectorstore"),
            embedding_function=embeddings,
            collection_name="faq_collection"
        )
        print("   ✅ 벡터 스토어 로드 성공")

        # 컬렉션 정보 확인
        collection = vectorstore._collection
        count = collection.count()
        print(f"   - 저장된 문서 수: {count}개")

    except Exception as e:
        print(f"   ❌ 벡터 스토어 로드 실패: {e}")
        return

    # 테스트 쿼리들
    test_queries = [
        "메신저 알림이 안 와요",
        "비밀번호를 잊어버렸어요",
        "파일 업로드가 안 됩니다",
        "로그인이 안돼요",
        "화면이 깨져요"
    ]

    print("\n2. 검색 테스트:")
    print("-" * 60)

    for query in test_queries:
        print(f"\n🔍 쿼리: '{query}'")

        try:
            # similarity_search_with_score 사용
            docs_with_scores = vectorstore.similarity_search_with_score(query, k=3)

            if not docs_with_scores:
                print("   ⚠️  검색 결과 없음")
                continue

            print(f"   ✅ {len(docs_with_scores)}개 결과 발견")

            for i, (doc, score) in enumerate(docs_with_scores, 1):
                print(f"\n   [{i}] 제목: {doc.metadata.get('title', 'N/A')}")
                print(f"       카테고리: {doc.metadata.get('category', 'N/A')}")
                print(f"       유사도 점수: {score:.4f} (낮을수록 유사)")
                print(f"       ID: {doc.metadata.get('id', 'N/A')}")

                # 내용 미리보기
                content_preview = doc.page_content[:150].replace('\n', ' ')
                print(f"       내용: {content_preview}...")

        except Exception as e:
            print(f"   ❌ 검색 실패: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)

if __name__ == "__main__":
    test_vectorstore_search()
