
import json
from typing import List
from charity_decision_system import (
    CharityAgent, GrantRequest, ProgramCategory, UrgencyLevel,
    AllocationDecision
)
from fund_allocator import FundAllocator
from topsis_analyzer import TOPSISAnalyzer


def print_header():
    print("\n" + "=" * 80)
    print(" " * 20 + "Hệ thống trợ giúp quyết định quỹ từ thiện")
    print("=" * 80)


def print_menu():
    print("\nMAIN MENU:")
    print("1. dữ liệu mẫu")
    print("2. Nhập só tiền yêu cầu từ thiện")
    print("3. Phân tích phân bổ")
    print("4. So sánh phương án")
    print("5. Xuất dưới dạng JSON")
    print("6. Yêu cầu hiện tại")
    print("7. Exit")
    print("-" * 80)


def get_urgency_level():
    print("\nMỨc độ cấp bách:")
    print("1. Nghiêm trọng (Cần ngay lập tức)")
    print("2. Cao (Cấp bch nhưng chưa cần ngay)")
    print("3. Trung bình (theo thời lượng tiêu chuẩn)")
    print("4. Thấp (Có thể trì hoãn)")
    print("5. Linh hoạt (Không giới hạn thời gian)")
    
    choice = input("Chọn mức độ cấo bách (1-5): ").strip()
    urgency_map = {
        '1': UrgencyLevel.CRITICAL,
        '2': UrgencyLevel.HIGH,
        '3': UrgencyLevel.MEDIUM,
        '4': UrgencyLevel.LOW,
        '5': UrgencyLevel.FLEXIBLE
    }
    return urgency_map.get(choice, UrgencyLevel.MEDIUM)


def get_program_category():
    print("\nLoại chương trình từ thiện:")
    print("1. Y tế")
    print("2. Giáo dục")
    print("3. Thực phẩm")
    print("4. Hỗ trợ thiên tai")
    print("5. Nhà ở")
    print("6. Môi trường")
    print("7. Khác")
    
    choice = input("Chọn (1-7): ").strip()
    category_map = {
        '1': ProgramCategory.HEALTHCARE,
        '2': ProgramCategory.EDUCATION,
        '3': ProgramCategory.FOOD_SECURITY,
        '4': ProgramCategory.DISASTER_RELIEF,
        '5': ProgramCategory.HOUSING,
        '6': ProgramCategory.ENVIRONMENT,
        '7': ProgramCategory.OTHER
    }
    return category_map.get(choice, ProgramCategory.OTHER)


def input_agent():
    print("\n" + "-" * 80)
    print("Thông tin tổ chức từ thiện")
    print("-" * 80)
    
    agent_id = input("ID: ").strip()
    name = input("Tên tổ chức từ thiện: ").strip()
    
    while True:
        try:
            success_rate = float(input("Lịch sử mức độ hoàn thành (0-1, vd., 0.85): ").strip())
            if 0 <= success_rate <= 1:
                break
            print("Error: Giá trị phải giữa 0 và 1")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    while True:
        try:
            transparency = float(input("Tính minh bạch (0-1, e.g., 0.90): ").strip())
            if 0 <= transparency <= 1:
                break
            print("Error: Giá trị phải giữa 0 và 1")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    while True:
        try:
            total_programs = int(input("Số lượng chưng trình đã hoàn thành: ").strip())
            if total_programs >= 0:
                break
            print("Error: Phải là số dương")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    while True:
        try:
            succeeded = int(input("Số lượng chương trình thành công: ").strip())
            if 0 <= succeeded <= total_programs:
                break
            print("Error: Giá trị phải giữa 0 và {total_programs}")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    return CharityAgent(
        agent_id=agent_id,
        name=name,
        success_rate=success_rate,
        transparency_score=transparency,
        total_programs_completed=total_programs,
        programs_succeeded=succeeded
    )


def input_grant_request(agent: CharityAgent):
    print("\n" + "-" * 80)
    print("Yêu cầu từ thiện")
    print("-" * 80)
    
    request_id = input("ID: ").strip()
    program_name = input("Tên chương trình từ thiện: ").strip()
    
    while True:
        try:
            amount = float(input("Khoảng tiền yêu cầu từ thiện ($): ").strip())
            if amount > 0:
                break
            print("Error: Phải là số dương")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    while True:
        try:
            overhead = float(input("Chi phí ($): ").strip())
            if 0 <= overhead < amount:
                break
            print("Error: Giá trị phải giữa 0 và {amount}")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    while True:
        try:
            people = int(input("Số lượng người hưởng lợi: ").strip())
            if people > 0:
                break
            print("Error: Phải là số dương")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    while True:
        try:
            duration = int(input("DThời lượng (tháng): ").strip())
            if duration > 0:
                break
            print("Error: Phải là số dương")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    category = get_program_category()
    urgency = get_urgency_level()
    
    location = input("Vị trí: ").strip()
    
    while True:
        try:
            sustainability = float(input("Tính bền vững (0-1, e.g., 0.75): ").strip())
            if 0 <= sustainability <= 1:
                break
            print("Error: Giá trị phải giữa 0 và 1")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    return GrantRequest(
        request_id=request_id,
        agent=agent,
        program_name=program_name,
        amount_requested=amount,
        overhead_cost=overhead,
        people_benefitted=people,
        duration_months=duration,
        category=category,
        urgency=urgency,
        geographic_location=location,
        sustainability_score=sustainability
    )


def view_requests(requests: List[GrantRequest]):
    if not requests:
        print("\nKhông có yêu cầu khoản từ thiện")
        return
    
    print("\n" + "=" * 80)
    print("Khoản từ thiện yêu cầu")
    print("=" * 80)
    
    total_requested = sum(r.amount_requested for r in requests)
    
    for i, req in enumerate(requests, 1):
        print(f"\n{i}. {req.program_name}")
        print(f"   Tổ chức: {req.agent.name}")
        print(f"   Yêu cầu: ${req.amount_requested:,.0f}")
        print(f"   Người hưởng: {req.people_benefitted:,}")
        print(f"   Chương trình: {req.category.value}")
        print(f"   Độ cấp bách: {req.urgency.name}")
    
    print(f"\nLượng từ thiện yêu cầu: ${total_requested:,.0f}")
    print("=" * 80)


def run_allocation_analysis(requests: List[GrantRequest]):
    if not requests:
        print("\nError: Không có yêu cầu khoản từ thiện.")
        return None
    
    print("\n" + "-" * 80)
    print("Phân tích phân bổ")
    print("-" * 80)
    
    while True:
        try:
            budget = float(input("\nQuỹ ($): ").strip())
            if budget > 0:
                break
            print("Error: Quỹ phải là số dương")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    while True:
        try:
            min_pct = float(input("Tỷ lệ phân bổ tối thiểu (0-1, vd, 0.5): ").strip())
            if 0 <= min_pct <= 1:
                break
            print("Error: Giá trị phaải nằm giữa 0 và 1")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    print("\nPhưng án phân bổ:")
    print("1. Greedy (Chỉ từ thiện toàn bộ)")
    print("2. Greedy (Cho phép từ thiện một phần)")
    print("3. Phân bổ theo tỷ lệ")
    print("4. Knapsack")
    
    strategy = input("\nSChọn phương án (1-4): ").strip()
    
    allocator = FundAllocator(total_budget=budget, min_allocation_percentage=min_pct)
    
    if strategy == '1':
        result = allocator.allocate_greedy(requests, allow_partial=False)
        strategy_name = "Greedy (Từ thiện toàn bộ)"
    elif strategy == '2':
        result = allocator.allocate_greedy(requests, allow_partial=True)
        strategy_name = "Greedy (Từ thiện một phần)"
    elif strategy == '3':
        result = allocator.allocate_proportional(requests)
        strategy_name = "Tỷ lệ"
    elif strategy == '4':
        result = allocator.allocate_knapsack(requests)
        strategy_name = "Knapsack"
    else:
        print("Không hợp lệ, chọn Greedy (Từ thiện một phần)")
        result = allocator.allocate_greedy(requests, allow_partial=True)
        strategy_name = "Greedy (Từ thiện một phần)"
    
    print("\n" + "=" * 80)
    print(f"Kết quả - {strategy_name}")
    print("=" * 80)
    print(result.summary())
    
    print("\nChi tiết lựa chọn:")
    print("-" * 80)
    
    for decision in sorted(result.decisions, key=lambda d: d.rank):
        symbol = "[FULL]" if decision.is_fully_funded() else "[PART]" if decision.is_partially_funded() else "[REJ]"
        print(f"\n{symbol} Rank #{decision.rank}: {decision.request.program_name}")
        print(f"   Phân bổ: ${decision.amount_allocated:,.0f} ({decision.allocation_percentage:.0%})")
        print(f"   Cơ sở: {decision.rationale}")
    
    print("\n" + "=" * 80)
    
    return result


def compare_strategies(requests: List[GrantRequest]):
    if not requests:
        print("\nError: Không có yêu cầu khoản từ thiện.")
        return
    
    while True:
        try:
            budget = float(input("\nTổng quỹ từ thiện ($): ").strip())
            if budget > 0:
                break
            print("Error: Quỹ phải là số dương")
        except ValueError:
            print("Error: Yêu cầu giá trị hợp lệ")
    
    allocator = FundAllocator(total_budget=budget)
    results = allocator.compare_strategies(requests)
    
    print("\n" + "=" * 80)
    print("So sánh phương án")
    print("=" * 80)
    
    for name, result in results.items():
        print(f"\n{name.upper()}:")
        print(f"  Phân bổ: ${result.total_allocated:,.0f} ({result.utilization_rate():.1f}%)")
        print(f"  Từ thiện hoàn toàn: {result.num_fully_funded}")
        print(f"  Từ thiện một phần: {result.num_partially_funded}")
        print(f"  Từ chối: {result.num_rejected}")
        print(f"  Số người hưởng lợi: {result.total_people_benefitted:,}")
        print(f"  Hiệu quả trung bình: {result.average_efficiency_ratio:.1%}")
    
    print("\n" + "=" * 80)


def export_results(result, filename: str = "allocation_results.json"):
    if result is None:
        print("\nError: Không có kết quả.")
        return
    
    output = {
        'quỹ': {
            'tổng': result.total_budget,
            'phân bố': result.total_allocated,
            'dư': result.remaining_budget,
            'tỷ lệ': result.utilization_rate()
        },
        'tổng kết': {
            'từ thiện hoa toàn': result.num_fully_funded,
            'từ thiện một phần': result.num_partially_funded,
            'từ chối': result.num_rejected,
            'số người hưởng lợi': result.total_people_benefitted,
            'hiệu quả trung bình': result.average_efficiency_ratio
        },
        'phương án': []
    }
    
    for decision in result.decisions:
        output['decisions'].append({
            'xếp hạng': decision.rank,
            'tên chương trình': decision.request.program_name,
            'tổ chức': decision.request.agent.name,
            'yêu cầu': decision.request.amount_requested,
            'phân bổ': decision.amount_allocated,
            'tỷ lệ phân bổ': decision.allocation_percentage,
            'mức độ cấp bách': decision.priority_score,
            'số người hưởng lợi': int(decision.request.people_benefitted * decision.allocation_percentage),
            'cơ sở': decision.rationale
        })
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[OK] Results exported to {filename}")


def main():
    print_header()
    
    requests = []
    last_result = None
    
    while True:
        print_menu()
        choice = input("Lựa chọn (1-7): ").strip()
        
        if choice == '1':
            from example_usage import create_sample_requests
            requests = create_sample_requests()
            print(f"\n[OK] {len(requests)} số lượng từ thiện yêu cầu(mẫu).")
        
        elif choice == '2':
            print("\nBạn muốn có bao nhiêu yêu cầu từ thiện?")
            try:
                num_requests = int(input("Số lượng yêu cầu: ").strip())
            except ValueError:
                print("Error: Yêu cầu không hợp lệ")
                continue
            
            requests = []
            agents = {}
            
            for i in range(num_requests):
                print(f"\n--- Yêu cầu thứ {i+1}/{num_requests} ---")
                
                print("\nBạn muốn:")
                print("1. Thêm tổ chức mới")
                print("2. Lựa chọn tổ chức có sẵn")
                
                agent_choice = input("Lựa chọn (1-2): ").strip()
                
                if agent_choice == '2' and agents:
                    print("\nCác tổ chức có sẵn:")
                    for idx, (aid, agent) in enumerate(agents.items(), 1):
                        print(f"{idx}. {agent.name} ({aid})")
                    
                    try:
                        agent_idx = int(input("Chọn tổ chức thứ (number): ").strip()) - 1
                        agent = list(agents.values())[agent_idx]
                    except (ValueError, IndexError):
                        print("Không hợp lệ. Thêm tổ chức mới.")
                        agent = input_agent()
                        agents[agent.agent_id] = agent
                else:
                    agent = input_agent()
                    agents[agent.agent_id] = agent
                
                request = input_grant_request(agent)
                requests.append(request)
            
            print(f"\n[OK] Đã thêm {len(requests)} yêu cầu.")
        
        elif choice == '3':
            last_result = run_allocation_analysis(requests)
        
        elif choice == '4':
            compare_strategies(requests)
        
        elif choice == '5':
            # Export results
            filename = input("\nOutput filename (default: allocation_results.json): ").strip()
            if not filename:
                filename = "allocation_results.json"
            export_results(last_result, filename)
        
        elif choice == '6':
            # View requests
            view_requests(requests)
        
        elif choice == '7':
            print("\nThoát")
            print("=" * 80 + "\n")
            break
        
        else:
            print("\nLựa chọn không hợp lệ")


if __name__ == "__main__":
    main()
