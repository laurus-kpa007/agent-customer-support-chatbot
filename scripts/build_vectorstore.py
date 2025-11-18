#!/usr/bin/env python3
"""벡터 스토어 구축 스크립트

FAQ JSON 파일을 읽어서 Chroma 벡터 스토어를 구축합니다.
문서 전체 청킹 전략을 사용하여 해결 방법이 잘리지 않도록 합니다.
"""

import json
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


def load_faq_data(file_path: str) -> list:
    """FAQ JSON 파일 로드"""
    print(f"📚 FAQ 데이터 로드 중... ({file_path})")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ {len(data)}개 FAQ 로드 완료")
    return data


def create_documents_from_faq(faq_data: list) -> list:
    """FAQ 데이터를 Document 객체로 변환 (전체 문서 청킹)

    청킹 전략: 각 FAQ 문서를 통째로 하나의 청크로 처리
    - 장점: 해결 방법이 절대 잘리지 않음
    - 적합성: FAQ 크기가 1000-2000자로 적당함
    """
    print("\n📄 Document 객체 생성 중...")
    documents = []

    for faq in faq_data:
        # 전체 FAQ 내용을 하나의 문자열로 구성
        content = f"""제목: {faq['title']}
카테고리: {faq['category']}

증상:
{faq['content']['symptom']}

원인:
{faq['content']['cause']}

해결 방법:
"""
        # 모든 해결 방법을 완전하게 포함
        for solution in faq['content']['solutions']:
            content += f"\n[방법 {solution['method']}] {solution['title']}\n"
            for i, step in enumerate(solution['steps'], 1):
                content += f"  {i}. {step}\n"
            content += f"  ▶ 기대 결과: {solution['expected_result']}\n"

        # Document 생성 (메타데이터 포함)
        doc = Document(
            page_content=content,
            metadata={
                "id": faq["id"],
                "category": faq["category"],
                "title": faq["title"],
                "tags": faq["tags"],
                "source": faq["source"],
                "helpful_count": faq["helpful_count"],
                "created_at": faq["created_at"]
            }
        )
        documents.append(doc)

    print(f"✅ {len(documents)}개 Document 생성 완료")
    print(f"   - 평균 길이: {sum(len(d.page_content) for d in documents) // len(documents)}자")
    print(f"   - 최대 길이: {max(len(d.page_content) for d in documents)}자")
    print(f"   - 최소 길이: {min(len(d.page_content) for d in documents)}자")

    return documents


def build_vectorstore(documents: list, persist_directory: str = "data/vectorstore") -> Chroma:
    """Chroma 벡터 스토어 구축"""

    # Ollama 임베딩 모델 로드
    print("\n🔄 Ollama 임베딩 모델 로드 중...")
    embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-m3-korean")
    print(f"   - 모델: {embedding_model}")

    try:
        embeddings = OllamaEmbeddings(model=embedding_model)
        print("✅ BGE-M3-Korean 임베딩 모델 로드 완료")
    except Exception as e:
        print(f"❌ 임베딩 모델 로드 실패: {e}")
        print("\n💡 Ollama 서버가 실행 중인지 확인하세요:")
        print("   ollama serve")
        print(f"\n💡 모델이 다운로드되었는지 확인하세요:")
        print(f"   ollama pull {embedding_model}")
        sys.exit(1)

    # Chroma 벡터 스토어 구축
    print(f"\n🗄️  Chroma 벡터 스토어 구축 중...")
    print(f"   - 저장 경로: {persist_directory}")
    print(f"   - 문서 수: {len(documents)}개")
    print(f"   - 임베딩 진행 중... (수 분 소요될 수 있습니다)")

    try:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="faq_collection"
        )
        print("✅ 벡터 스토어 구축 완료")
    except Exception as e:
        print(f"❌ 벡터 스토어 구축 실패: {e}")
        sys.exit(1)

    return vectorstore


def test_search(vectorstore: Chroma):
    """벡터 검색 테스트"""
    print("\n🔍 테스트 검색 수행 중...")

    test_queries = [
        "메신저에서 알림이 안떠요",
        "비밀번호를 잊어버렸어요",
        "파일 업로드가 안돼요"
    ]

    for query in test_queries:
        print(f"\n📌 쿼리: {query}")
        results = vectorstore.similarity_search(query, k=2)

        for i, doc in enumerate(results, 1):
            print(f"\n   [{i}] {doc.metadata['title']}")
            print(f"       카테고리: {doc.metadata['category']}")
            print(f"       ID: {doc.metadata['id']}")
            # 내용 미리보기 (처음 100자)
            preview = doc.page_content.replace('\n', ' ')[:100]
            print(f"       내용: {preview}...")


def main():
    """메인 함수"""
    print("="*60)
    print("  FAQ 벡터 스토어 구축 스크립트")
    print("  - 전략: 문서 전체 청킹 (해결 방법 완전 보존)")
    print("  - 벡터 DB: Chroma")
    print("  - 임베딩: Ollama BGE-M3-Korean")
    print("="*60)

    # FAQ 데이터 로드
    faq_file = "data/faq_sample.json"
    if not os.path.exists(faq_file):
        print(f"❌ FAQ 파일을 찾을 수 없습니다: {faq_file}")
        sys.exit(1)

    faq_data = load_faq_data(faq_file)

    # Document 객체 생성
    documents = create_documents_from_faq(faq_data)

    # 벡터 스토어 구축
    vectorstore = build_vectorstore(documents)

    # 테스트 검색
    test_search(vectorstore)

    print("\n" + "="*60)
    print("✅ 벡터 스토어 구축 완료!")
    print("="*60)
    print(f"\n저장 위치: {os.path.abspath('data/vectorstore')}")
    print("\n이제 챗봇을 실행할 수 있습니다:")
    print("  streamlit run src/ui/app.py")


if __name__ == "__main__":
    main()
