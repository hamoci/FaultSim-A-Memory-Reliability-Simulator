#!/usr/bin/env python3
"""
FaultSim 로그 파일 파싱 스크립트
각 ECC 종류와 용량별 CE, UE, SDC, 총 Error 수를 추출합니다.
"""

import os
import re
import glob

def parse_log_file(log_file_path):
    """
    로그 파일의 마지막 부분에서 failed_sims, sims, rate_uncorr, rate_undet를 파싱하여
    CE, UE, SDC, 총 Error 수를 계산
    """
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # MODULE0 전체 통계 라인 찾기
        # 예: [MODULE0] sims 1000000 failed_sims 112090 rate_raw 0.11209 FIT_raw 1827.95 rate_uncorr 0.000747 FIT_uncorr 12.182 rate_undet 1.6e-05 FIT_undet 0.260926
        module_pattern = r'\[MODULE0\]\s+sims\s+(\d+)\s+failed_sims\s+(\d+)\s+rate_raw\s+[\d\.e\-+]+\s+FIT_raw\s+[\d\.e\-+]+\s+rate_uncorr\s+([\d\.e\-+]+)\s+FIT_uncorr\s+[\d\.e\-+]+\s+rate_undet\s+([\d\.e\-+]+)'
        match = re.search(module_pattern, content)
        
        if not match:
            return None
            
        sims = int(match.group(1))
        failed_sims = int(match.group(2))
        rate_uncorr = float(match.group(3))
        rate_undet = float(match.group(4))
        
        # 계산
        # Total = failed_sims
        # rate_uncorr: uncorrectable error rate (전체 UE)
        # rate_undet: undetected error rate (SDC, UE의 부분집합)
        # 
        # 서로 배타적인 분류:
        # CE (Correctable Errors) = failed_sims - (전체 UE)
        # DUE (Detected Uncorrectable Error) = (전체 UE) - SDC
        # SDC (Silent Data Corruption) = undetected errors
        total = failed_sims
        total_ue = int(sims * rate_uncorr)
        sdc = int(sims * rate_undet)
        due = total_ue - sdc  # Detected Uncorrectable Error
        ce = total - total_ue
        ue_sdc = due + sdc  # UE + SDC (critical errors causing system failure)
        critical_error_rate = ue_sdc / sims if sims > 0 else 0  # Probability of critical error
        
        return {
            'ce': ce,
            'ue': due,  # DUE (감지된 수정 불가 에러)
            'sdc': sdc,
            'ue_sdc': ue_sdc,
            'critical_error_rate': critical_error_rate,
            'total': total
        }
        
    except Exception as e:
        print(f"Error parsing {log_file_path}: {e}")
        return None

def extract_config_info_from_filename(filename):
    """
    파일명에서 ECC 타입과 용량 정보를 추출
    예: dimm_secded_32gb_log.txt -> ('SECDED', '32GB')
    """
    # 기본 파일명 패턴: dimm_[ecc_type]_[capacity]_log.txt
    match = re.match(r'dimm_([^_]+)(?:_(\d+gb))?_log\.txt', filename.lower())
    
    if not match:
        return None, None
        
    ecc_type = match.group(1).upper()
    capacity = match.group(2).upper() if match.group(2) else "2GB"  # 기본값
    
    # ECC 타입 정규화
    if ecc_type == 'SECDED':
        ecc_type = 'SECDED'
    elif ecc_type == 'CHIPKILL':
        ecc_type = 'ChipKill'
    elif ecc_type == 'NONE':
        ecc_type = 'No ECC'
    
    return ecc_type, capacity

def main():
    """
    메인 함수: results 디렉토리의 모든 로그 파일을 파싱하고 결과 출력
    """
    results_dir = "/home/hamoci/Study/FaultSim-A-Memory-Reliability-Simulator/results"
    
    # 모든 로그 파일 찾기
    log_files = glob.glob(os.path.join(results_dir, "*_log.txt"))
    
    if not log_files:
        print("로그 파일을 찾을 수 없습니다.")
        return
    
    # 결과 저장할 리스트
    results = []
    
    print("로그 파일 파싱 중...")
    for log_file in sorted(log_files):
        filename = os.path.basename(log_file)
        print(f"처리 중: {filename}")
        
        # 파일명에서 정보 추출
        ecc_type, capacity = extract_config_info_from_filename(filename)
        
        if not ecc_type or not capacity:
            print(f"  - 파일명 형식을 인식할 수 없습니다: {filename}")
            continue
            
        # 로그 파일 파싱
        stats = parse_log_file(log_file)
        
        if stats is None:
            print(f"  - MODULE0 통계를 찾을 수 없습니다: {filename}")
            continue
            
        results.append({
            'ecc_type': ecc_type,
            'capacity': capacity,
            'ce': stats['ce'],
            'ue': stats['ue'], 
            'sdc': stats['sdc'],
            'ue_sdc': stats['ue_sdc'],
            'critical_error_rate': stats['critical_error_rate'],
            'total': stats['total']
        })
        
        print(f"  - 파싱 완료: {ecc_type}, {capacity}")
    
    # 결과 출력
    print("\n" + "="*100)
    print("FaultSim 에러 통계 결과")
    print("="*100)
    print(f"{'ECC Type':<12} {'Capacity':<8} {'CE':<8} {'UE':<8} {'SDC':<8} {'UE+SDC':<8} {'Crit.Rate':<12} {'Total':<10}")
    print("-"*100)
    
    # ECC 타입별, 용량별로 정렬
    def sort_key(item):
        # ECC 타입 순서: No ECC -> SECDED -> ChipKill
        ecc_order = {'No ECC': 0, 'SECDED': 1, 'ChipKill': 2}
        ecc_priority = ecc_order.get(item['ecc_type'], 3)
        
        # 용량 순서: 숫자로 변환해서 정렬
        capacity_num = 0
        if item['capacity'].replace('GB', '').replace('.', '').isdigit():
            capacity_num = float(item['capacity'].replace('GB', ''))
            
        return (ecc_priority, capacity_num)
    
    results.sort(key=sort_key)
    
    for result in results:
        print(f"{result['ecc_type']:<12} {result['capacity']:<8} "
              f"{result['ce']:<8} {result['ue']:<8} {result['sdc']:<8} "
              f"{result['ue_sdc']:<8} {result['critical_error_rate']:<12.6e} {result['total']:<10}")
    
    # ECC 타입별 평균 비율 계산 및 출력
    print("\n" + "="*80)
    print("ECC 타입별 에러 분포 비율 (평균)")
    print("="*80)
    
    ecc_stats = {}
    for result in results:
        ecc_type = result['ecc_type']
        if ecc_type not in ecc_stats:
            ecc_stats[ecc_type] = {'ce': 0, 'ue': 0, 'sdc': 0, 'total': 0, 'count': 0}
        
        ecc_stats[ecc_type]['ce'] += result['ce']
        ecc_stats[ecc_type]['ue'] += result['ue']
        ecc_stats[ecc_type]['sdc'] += result['sdc']
        ecc_stats[ecc_type]['total'] += result['total']
        ecc_stats[ecc_type]['count'] += 1
    
    for ecc_type in ['No ECC', 'SECDED', 'ChipKill']:
        if ecc_type in ecc_stats:
            stats = ecc_stats[ecc_type]
            total = stats['total']
            ce_pct = (stats['ce'] / total * 100) if total > 0 else 0
            ue_pct = (stats['ue'] / total * 100) if total > 0 else 0
            sdc_pct = (stats['sdc'] / total * 100) if total > 0 else 0
            
            print(f"- {ecc_type}: CE {ce_pct:.2f}%, UE {ue_pct:.2f}%, SDC {sdc_pct:.2f}%")
    
    # 용량별 Total 증가율 출력
    print("\n" + "="*80)
    print("용량별 Total Errors 증가 추이")
    print("="*80)
    
    for ecc_type in ['No ECC', 'SECDED', 'ChipKill']:
        ecc_results = [r for r in results if r['ecc_type'] == ecc_type]
        if ecc_results:
            print(f"\n{ecc_type}:")
            base_total = None
            base_capacity = None
            
            for result in ecc_results:
                capacity_str = result['capacity']
                capacity_gb = float(capacity_str.replace('GB', ''))
                total = result['total']
                
                if base_total is None:
                    base_total = total
                    base_capacity = capacity_gb
                    print(f"  {capacity_str:>8}: {total:>8} errors (baseline)")
                else:
                    increase_ratio = total / base_total
                    capacity_ratio = capacity_gb / base_capacity
                    print(f"  {capacity_str:>8}: {total:>8} errors (×{increase_ratio:.2f}, 용량 ×{capacity_ratio:.2f})")
    
    print("\n파싱 완료! 총 {} 개의 로그 파일을 처리했습니다.".format(len(results)))
    
    # CSV 파일로도 저장
    csv_filename = "faultsim_error_statistics.csv"
    try:
        with open(csv_filename, 'w', encoding='utf-8') as f:
            # 헤더 작성
            f.write("ECC Type,Capacity,CE,UE,SDC,UE+SDC,Critical Error Rate,Total\n")
            
            # 데이터 작성
            for result in results:
                f.write(f"{result['ecc_type']},{result['capacity']},{result['ce']},{result['ue']},{result['sdc']},"
                       f"{result['ue_sdc']},{result['critical_error_rate']:.10f},{result['total']}\n")
        
        print(f"\nCSV 파일로도 저장했습니다: {csv_filename}")
        
    except Exception as e:
        print(f"CSV 파일 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    main()