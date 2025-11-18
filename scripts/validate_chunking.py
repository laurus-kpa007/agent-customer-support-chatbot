#!/usr/bin/env python3
"""청킹 품질 검증 스크립트

벡터 스토어의 각 문서에서 해결 방법이 완전한지 검증합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()


def validate_chunking_completeness():
    """청킹 전략 검증: 해결 방법이 완전한지 확인"""

    print("="*60)
    print("  청킹 품질 검증")
    print("  - 각 FAQ의 해결 방법이 완전한지 확인합니다")
    print("="*60)

    # 벡터 스토어 로드
    print("\n📂 벡터 스토어 로드 중...")
    embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-m3-korean")

    try:
        embeddings = OllamaEmbeddings(model=embedding_model)
        vectorstore = Chroma(
            persist_directory="data/vectorstore",
            embedding_function=embeddings,
            collection_name="faq_collection"
        )
        print("✅ 벡터 스토어 로드 완료")
    except Exception as e:
        print(f"❌ 벡터 스토어 로드 실패: {e}")
        print("\n💡 먼저 벡터 스토어를 구축하세요:")
        print("   python scripts/build_vectorstore.py")
        sys.exit(1)

    # 테스트 쿼리
    test_cases = [
        "메신저 알림 설정",
        "로그인 비밀번호 오류",
        "파일 업로드 실패",
        "화면이 검게 나옴",
        "계정 잠금"
    ]

    print("\n🔍 청킹 완전성 검증 중...\n")

    total_tests = len(test_cases)
    passed_tests = 0

    for query in test_cases:
        print(f"쿼리: {query}")
        results = vectorstore.similarity_search(query, k=1)

        if not results:
            print(f"  ⚠️  검색 결과 없음")
            print()
            continue

        doc = results[0]
        content = doc.page_content

        # 해결 방법이 완전한지 확인
        method_count = content.count("[방법")
        expected_result_count = content.count("▶ 기대 결과:")

        print(f"  - 문서 ID: {doc.metadata.get('id', 'N/A')}")
        print(f"  - 제목: {doc.metadata.get('title', 'N/A')}")
        print(f"  - 발견된 방법 수: {method_count}")
        print(f"  - 완전한 방법 수: {expected_result_count}")

        if method_count == expected_result_count and method_count > 0:
            print(f"  ✅ 모든 해결 방법이 완전함")
            passed_tests += 1
        else:
            print(f"  ⚠️  경고: 불완전한 해결 방법 발견!")

        print()

    # 요약
    print("="*60)
    print(f"검증 결과: {passed_tests}/{total_tests} 테스트 통과")
    if passed_tests == total_tests:
        print("✅ 모든 FAQ 문서의 해결 방법이 완전합니다!")
    else:
        print("⚠️  일부 문서에서 문제가 발견되었습니다.")
    print("="*60)


if __name__ == "__main__":
    validate_chunking_completeness()
