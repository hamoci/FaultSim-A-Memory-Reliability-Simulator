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
    """개선된 요약 차트 with Error Rate overlay"""
    df = pd.read_csv('faultsim_error_statistics.csv')
    df['capacity_num'] = df['Capacity'].apply(parse_capacity)
    
    fig, ax1 = plt.subplots(1, 1, figsize=(18, 8))
    
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
    
    # ECC 타입별 마커 스타일 (점 모양과 색상)
    marker_styles = {
        'No ECC': {'marker': 's', 'color': '#FF0000', 'size': 100},      # 네모, 빨강
        'SECDED': {'marker': 'o', 'color': '#0000FF', 'size': 100},      # 동그라미, 파랑
        'ChipKill': {'marker': '*', 'color': '#00AA00', 'size': 150}     # 별, 초록
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
        bars_ce = ax1.bar(x_pos, ce_values, bar_width, 
                        label='CE' if ecc_idx == 0 else "", 
                        color=colors['CE'], 
                        alpha=0.9, edgecolor='black', linewidth=0.5)
        
        # UE 막대 (CE 위에 스택)
        bars_ue = ax1.bar(x_pos, ue_values, bar_width,
                        bottom=ce_values,
                        label='UE' if ecc_idx == 0 else "",
                        color=colors['UE'],
                        alpha=0.9, edgecolor='black', linewidth=0.5)
        
        # SDC 막대 (CE+UE 위에 스택)
        bars_sdc = ax1.bar(x_pos, sdc_values, bar_width,
                         bottom=ce_values + ue_values,
                         label='SDC' if ecc_idx == 0 else "",
                         color=colors['SDC'],
                         alpha=0.9, edgecolor='black', linewidth=0.5)
        
        # 총합 표시 (막대 위에)
        for i, (bar_ce, total) in enumerate(zip(bars_ce, total_values)):
            x_center = bar_ce.get_x() + bar_ce.get_width()/2
            ax1.text(x_center, total + total*0.01,
                   f'{int(total):,}', ha='center', va='bottom', 
                   fontsize=8, fontweight='bold', color='black')
    
    # ECC 타입 레이블을 그래프 영역 밖 (x축 아래)에 첫 번째 그룹에만 표시
    for ecc_idx, ecc_type in enumerate(ecc_types):
        x_pos = x_positions + (ecc_idx - 1) * bar_width
        if ecc_idx < len(ecc_types):  # 첫 번째 용량의 모든 ECC 타입 표시
            ax1.text(x_pos[0], ax1.get_ylim()[0] - (ax1.get_ylim()[1] - ax1.get_ylim()[0])*0.08, ecc_type,
                   ha='center', va='top', fontsize=8, fontweight='bold',
                   rotation=0, color='black', transform=ax1.transData)
    
    # 축 설정
    ax1.set_xlabel('Memory Capacity', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Errors', fontsize=14, fontweight='bold')
    
    # x축 레이블을 용량만 표시 (ECC 타입은 막대 아래에 표시됨)
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(capacities, fontsize=12, fontweight='bold')
    
    # y축 범위 설정 (정상 범위로)
    max_total = df['Total'].max()
    ax1.set_ylim(0, max_total*1.1)
    
    # 그리드 설정
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_axisbelow(True)
    
    # 두 번째 y축 생성 (Error Rate용)
    ax2 = ax1.twinx()
    
    # y2축 범위 계산 (퍼센트가 아닌 실제 비율로)
    max_rate = df['Critical Error Rate'].max()
    
    # 각 ECC 타입별로 Error Rate 점만 그리기 (선 없이)
    for ecc_idx, ecc_type in enumerate(ecc_types):
        data = df[df['ECC Type'] == ecc_type]
        data_sorted = data.set_index('Capacity').reindex(capacities)
        
        # 각 용량별 x 위치
        x_pos = x_positions + (ecc_idx - 1) * bar_width
        
        # Critical Error Rate를 실제 비율로 (퍼센트 변환 안 함)
        error_rate = data_sorted['Critical Error Rate'].values
        
        style = marker_styles[ecc_type]
        
        # 점만 표시 (선 없이)
        ax2.scatter(x_pos, error_rate, 
                   marker=style['marker'], s=style['size'],
                   color=style['color'], 
                   label=f'{ecc_type} Error Rate',
                   alpha=0.85, edgecolors='black', linewidths=1.5, zorder=5)
        
        # 각 점에 지수 표기법으로 값 표시 (점 아래에)
        for i, (x, rate) in enumerate(zip(x_pos, error_rate)):
            if not np.isnan(rate):
                # y 오프셋을 음수로 설정하여 아래에 표시
                y_offset = max_rate * 0.015  # 전체 범위의 1.5% 아래로
                ax2.text(x, rate - y_offset, f'{rate:.2e}', 
                        ha='center', va='top', fontsize=7,
                        fontweight='bold', color=style['color'])
    
    ax2.set_ylabel('Critical Error Rate', fontsize=14, fontweight='bold', color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # y2축 범위 설정
    ax2.set_ylim(0, max_rate * 1.25)  # 텍스트 공간을 위해 여유 확보
    
    # y2축을 지수 표기법으로 설정
    from matplotlib.ticker import ScalarFormatter
    formatter = ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-2, 2))
    ax2.yaxis.set_major_formatter(formatter)
    
    # 범례 합치기
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, 
              loc='upper left', fontsize=10, bbox_to_anchor=(0, 1))
    
    plt.subplots_adjust(bottom=0.15, right=0.88)
    plt.tight_layout()
    return fig

def main():
    """메인 함수 - 에러 개수와 에러율을 하나의 차트에 표시"""
    plt.rcParams['figure.figsize'] = (18, 8)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.style.use('default')
    
    print("Creating combined chart with error counts and rates...")
    fig = create_improved_summary_chart()
    fig.savefig('error_stats_combined.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print("\n" + "="*60)
    print("Visualization completed!")
    print("Generated file:")
    print("- error_stats_combined.png")
    print("\nChart includes:")
    print("- Bar chart: CE, UE, SDC error counts (left y-axis)")
    print("- Line plot: Critical Error Rate % (right y-axis)")
    print("- Critical Error Rate = (UE + SDC) / Total Simulations × 100%")

if __name__ == "__main__":
    main()