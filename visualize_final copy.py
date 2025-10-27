#!/usr/bin/env python3
"""
FaultSim Error Statistics - Improved Summary Chart
개선된 단일 요약 차트: 깔끔한 x축 레이블과 ECC 타입 표시
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def setup_matplotlib():
    """matplotlib 설정"""
    plt.rcParams['figure.figsize'] = (16, 10)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.style.use('default')

def parse_capacity(capacity_str):
    """용량 문자열을 숫자로 변환"""
    if 'GB' in capacity_str:
        num = capacity_str.replace('GB', '')
        return float(num) if '.' in num else int(num)
    return 0

def create_improved_summary_chart():
    """개선된 요약 차트"""
    df = pd.read_csv('faultsim_error_statistics.csv')
    df['capacity_num'] = df['Capacity'].apply(parse_capacity)
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 6))  # 세로 길이 더 단축
    
    capacities = sorted(df['Capacity'].unique(), key=parse_capacity)
    ecc_types = ['No ECC', 'SECDED', 'ChipKill']
    
    # 스택 바 차트로 구성 비율 표시
    n_capacities = len(capacities)
    n_ecc_types = len(ecc_types)
    
    # 전체 그룹 간격과 막대 너비 설정
    group_width = 0.8
    bar_width = group_width / n_ecc_types
    
    # x 위치 계산 (각 용량별로 3개 막대가 그룹을 이룸)
    x_positions = np.arange(n_capacities)
    
    # 색상 설정 - 흑백 명도차로 변경
    colors = {
        'CE': '#F0F0F0',    # 연한 회색 (가장 밝음)
        'UE': '#A0A0A0',    # 중간 회색
        'SDC': '#404040'    # 진한 회색 (가장 어두움)
    }
    
    # 각 ECC 타입별로 막대 그리기
    for ecc_idx, ecc_type in enumerate(ecc_types):
        data = df[df['ECC Type'] == ecc_type]
        data_sorted = data.set_index('Capacity').reindex(capacities)
        
        # 각 용량별 x 위치
        x_pos = x_positions + (ecc_idx - 1) * bar_width
        
        # 스택 바 생성
        ce_values = data_sorted['CE'].values
        ue_values = data_sorted['UE'].values  
        sdc_values = data_sorted['SDC'].values
        total_values = data_sorted['Total'].values
        
        # CE 막대
        bars_ce = ax.bar(x_pos, ce_values, bar_width, 
                        label='CE' if ecc_idx == 0 else "", 
                        color=colors['CE'], 
                        alpha=0.9, edgecolor='black', linewidth=0.5)
        
        # UE 막대 (CE 위에 스택)
        bars_ue = ax.bar(x_pos, ue_values, bar_width,
                        bottom=ce_values,
                        label='UE' if ecc_idx == 0 else "",
                        color=colors['UE'],
                        alpha=0.9, edgecolor='black', linewidth=0.5)
        
        # SDC 막대 (CE+UE 위에 스택)
        bars_sdc = ax.bar(x_pos, sdc_values, bar_width,
                         bottom=ce_values + ue_values,
                         label='SDC' if ecc_idx == 0 else "",
                         color=colors['SDC'],
                         alpha=0.9, edgecolor='black', linewidth=0.5)
        
        # 총합 표시 (막대 위에)
        for i, (bar_ce, total) in enumerate(zip(bars_ce, total_values)):
            x_center = bar_ce.get_x() + bar_ce.get_width()/2
            ax.text(x_center, total + total*0.01,
                   f'{int(total):,}', ha='center', va='bottom', 
                   fontsize=8, fontweight='bold', color='black')
    
    # ECC 타입 레이블을 그래프 영역 밖 (x축 아래)에 첫 번째 그룹에만 표시
    for ecc_idx, ecc_type in enumerate(ecc_types):
        x_pos = x_positions + (ecc_idx - 1) * bar_width
        if ecc_idx < len(ecc_types):  # 첫 번째 용량의 모든 ECC 타입 표시
            ax.text(x_pos[0], ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0])*0.08, ecc_type,
                   ha='center', va='top', fontsize=8, fontweight='bold',
                   rotation=0, color='black', transform=ax.transData)
    
    # 축 설정
    ax.set_xlabel('Memory Capacity', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Errors', fontsize=14, fontweight='bold')
    
    # x축 레이블을 용량만 표시 (ECC 타입은 막대 아래에 표시됨)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(capacities, fontsize=12, fontweight='bold')
    
    # y축 범위 설정 (정상 범위로)
    max_total = df['Total'].max()
    ax.set_ylim(0, max_total*1.1)
    
    # 범례를 그래프 오른쪽 위 바깥으로 이동
    ax.legend(loc='best', bbox_to_anchor=(1, 1), fontsize=10)
    
    # 그리드 설정
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_axisbelow(True)
    
    plt.subplots_adjust(bottom=0.15, right=0.85)  # 범례 공간 확보
    plt.tight_layout()
    return fig

def main():
    """메인 함수 - summary 차트만 생성"""
    plt.rcParams['figure.figsize'] = (18, 6)  # 세로 길이 더 단축
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.style.use('default')
    
    print("Creating improved summary chart...")
    fig = create_improved_summary_chart()
    fig.savefig('error_stats_summary_improved.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n" + "="*60)
    print("Improved summary visualization completed!")
    print("Generated file:")
    print("- error_stats_summary_improved.png")
    print("\nKey improvements:")
    print("- Cleaner x-axis with capacity labels")
    print("- ECC type labels only at first capacity group") 
    print("- Standard legend format")
    print("- Removed floating chart effect")
    print("- Removed analysis text box for cleaner look")

if __name__ == "__main__":
    main()