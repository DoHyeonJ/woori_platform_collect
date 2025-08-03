import asyncio
from datetime import datetime, timedelta
from data_collector import DataCollector

async def main():
    print("🚀 강남언니 데이터 수집기 시작")
    print("=" * 50)
    
    collector = DataCollector()
    
    # 카테고리 정의
    categories = {
        "hospital_question": "병원질문",
        "surgery_question": "시술/수술질문", 
        "free_chat": "자유수다",
        "review": "발품후기",
        "ask_doctor": "의사에게 물어보세요"
    }
    
    print("📂 수집할 카테고리:")
    for key, name in categories.items():
        print(f"   • {name}")
    print()
    
    # 날짜 선택
    print("📅 수집할 날짜를 선택하세요:")
    print("1. 오늘")
    print("2. 어제")
    print("3. 특정 날짜 입력")
    print("4. 최근 7일")
    
    choice = input("\n선택 (1-4): ").strip()
    
    if choice == "1":
        target_date = datetime.now().strftime("%Y-%m-%d")
        print(f"📅 오늘 ({target_date}) 데이터를 수집합니다.")
        
    elif choice == "2":
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"📅 어제 ({target_date}) 데이터를 수집합니다.")
        
    elif choice == "3":
        target_date = input("날짜를 입력하세요 (YYYY-MM-DD): ").strip()
        if not target_date:
            print("❌ 날짜를 입력해주세요.")
            return
        print(f"📅 {target_date} 데이터를 수집합니다.")
        
    elif choice == "4":
        print("📅 최근 7일 데이터를 수집합니다.")
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            print(f"\n--- {date} 수집 중 ---")
            try:
                articles_count, comments_count = await collector.collect_and_save_articles(date, categories)
                print(f"✅ {date}: 게시글 {articles_count}개, 댓글 {comments_count}개 수집 완료")
            except Exception as e:
                print(f"❌ {date} 수집 실패: {e}")
        
        # 최종 통계
        stats = collector.get_statistics()
        print(f"\n📊 최종 통계:")
        print(f"전체 게시글: {stats['total_articles']}개")
        print(f"전체 댓글: {stats['total_comments']}개")
        print(f"카테고리별 통계: {stats['category_stats']}")
        return
        
    else:
        print("❌ 올바른 선택지를 입력해주세요.")
        return
    
    # 데이터 수집 실행
    print("\n🔄 데이터 수집을 시작합니다...")
    try:
        articles_count, comments_count = await collector.collect_and_save_articles(target_date, categories)
        
        print(f"\n✅ 수집 완료!")
        print(f"📝 게시글: {articles_count}개")
        print(f"💬 댓글: {comments_count}개")
        
        # 통계 조회
        stats = collector.get_statistics()
        print(f"\n📊 데이터베이스 통계:")
        print(f"전체 게시글: {stats['total_articles']}개")
        print(f"전체 댓글: {stats['total_comments']}개")
        print(f"오늘 게시글: {stats['today_articles']}개")
        print(f"카테고리별 통계: {stats['category_stats']}")
        
    except Exception as e:
        print(f"❌ 데이터 수집 중 오류 발생: {e}")
    
    print("\n🎉 작업이 완료되었습니다!")

if __name__ == "__main__":
    asyncio.run(main()) 