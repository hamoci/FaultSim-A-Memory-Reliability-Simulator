#!/usr/bin/env python3
"""
FaultSim Error Statistics Visualization
CSV 파일에서 용량별 ECC 타입별 CE/UE/SDC 통계를 그래프로 시각화
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

def setup_matplotlib():
    """matplotlib 한글 폰트 설정"""
    plt.rcParams['figure.figsize'] = (15, 10)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    
    # 한글 폰트 시도 (시스템에 따라 다름)
    try:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    except:
        pass

def parse_capacity(capacity_str):
    """용량 문자열을 숫자로 변환 (정렬용)"""
    if 'GB' in capacity_str:
        num = capacity_str.replace('GB', '')
        if '.' in num:
            return float(num)
        else:
            return int(num)
    return 0

def load_and_process_data(csv_file):
    """CSV 파일 로드 및 전처리"""
    df = pd.read_csv(csv_file)
    
    # 용량별 정렬을 위한 숫자 컬럼 추가
    df['capacity_num'] = df['Capacity'].apply(parse_capacity)
    df = df.sort_values(['ECC Type', 'capacity_num'])
    
    print("데이터 미리보기:")
    print(df.head())
    print(f"\n총 {len(df)}개 데이터")
    print(f"ECC 타입: {df['ECC Type'].unique()}")
    print(f"용량: {sorted(df['Capacity'].unique(), key=parse_capacity)}")
    
    return df

def create_subplot_by_error_type(df):
    """에러 타입별로 서브플롯 생성"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('FaultSim Error Statistics by Memory Capacity and ECC Type', fontsize=16, fontweight='bold')
    
    # 용량 순서 정렬
    capacities = sorted(df['Capacity'].unique(), key=parse_capacity)
    ecc_types = ['No ECC', 'SECDED', 'ChipKill']
    colors = {'No ECC': 'red', 'SECDED': 'blue', 'ChipKill': 'green'}
    
    # CE 그래프
    ax1 = axes[0, 0]
    for ecc_type in ecc_types:
        data = df[df['ECC Type'] == ecc_type]
        data_sorted = data.set_index('Capacity').reindex(capacities)
        ax1.plot(capacities, data_sorted['CE'], marker='o', linewidth=2, label=ecc_type, color=colors[ecc_type])
    ax1.set_title('Correctable Errors (CE)', fontweight='bold')
    ax1.set_xlabel('Memory Capacity')
    ax1.set_ylabel('Number of CE')
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    
    # UE 그래프
    ax2 = axes[0, 1]
    for ecc_type in ecc_types:
        data = df[df['ECC Type'] == ecc_type]
        data_sorted = data.set_index('Capacity').reindex(capacities)
        ax2.plot(capacities, data_sorted['UE'], marker='s', linewidth=2, label=ecc_type, color=colors[ecc_type])
    ax2.set_title('Uncorrectable Errors (UE)', fontweight='bold')
    ax2.set_xlabel('Memory Capacity')
    ax2.set_ylabel('Number of UE')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    
    # SDC 그래프
    ax3 = axes[1, 0]
    for ecc_type in ecc_types:
        data = df[df['ECC Type'] == ecc_type]
        data_sorted = data.set_index('Capacity').reindex(capacities)
        ax3.plot(capacities, data_sorted['SDC'], marker='^', linewidth=2, label=ecc_type, color=colors[ecc_type])
    ax3.set_title('Silent Data Corruptions (SDC)', fontweight='bold')
    ax3.set_xlabel('Memory Capacity')
    ax3.set_ylabel('Number of SDC')
    ax3.legend()
    ax3.tick_params(axis='x', rotation=45)
    
    # 총 에러 그래프
    ax4 = axes[1, 1]
    for ecc_type in ecc_types:
        data = df[df['ECC Type'] == ecc_type]
        data_sorted = data.set_index('Capacity').reindex(capacities)
        ax4.plot(capacities, data_sorted['Total'], marker='d', linewidth=2, label=ecc_type, color=colors[ecc_type])
    ax4.set_title('Total Errors', fontweight='bold')
    ax4.set_xlabel('Memory Capacity')
    ax4.set_ylabel('Total Number of Errors')
    ax4.legend()
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig

def create_stacked_bar_chart(df):
    """ECC 타입별 스택 바 차트"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Error Distribution by ECC Type and Memory Capacity', fontsize=16, fontweight='bold')
    
    capacities = sorted(df['Capacity'].unique(), key=parse_capacity)
    ecc_types = ['No ECC', 'SECDED', 'ChipKill']
    
    for i, ecc_type in enumerate(ecc_types):
        ax = axes[i]
        data = df[df['ECC Type'] == ecc_type]
        data_sorted = data.set_index('Capacity').reindex(capacities)
        
        x = np.arange(len(capacities))
        width = 0.6
        
        # 스택 바 차트
        p1 = ax.bar(x, data_sorted['CE'], width, label='CE', color='lightblue')
        p2 = ax.bar(x, data_sorted['UE'], width, bottom=data_sorted['CE'], label='UE', color='orange')
        p3 = ax.bar(x, data_sorted['SDC'], width, 
                   bottom=data_sorted['CE'] + data_sorted['UE'], label='SDC', color='red')
        
        ax.set_title(f'{ecc_type}', fontweight='bold')
        ax.set_xlabel('Memory Capacity')
        ax.set_ylabel('Number of Errors')
        ax.set_xticks(x)
        ax.set_xticklabels(capacities, rotation=45)
        ax.legend()
        
        # 값 표시
        for j, capacity in enumerate(capacities):
            total = data_sorted.loc[capacity, 'Total']
            if total > 0:
                ax.text(j, total + total * 0.01, f'{total:,}', 
                       ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    return fig

def create_heatmap(df):
    """히트맵으로 에러 분포 시각화"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Error Distribution Heatmap', fontsize=16, fontweight='bold')
    
    # 피벗 테이블 생성
    capacities = sorted(df['Capacity'].unique(), key=parse_capacity)
    ecc_types = ['No ECC', 'SECDED', 'ChipKill']
    
    error_types = ['CE', 'UE', 'SDC', 'Total']
    
    for i, error_type in enumerate(error_types):
        ax = axes[i//2, i%2]
        
        # 피벗 테이블 생성
        pivot_data = df.pivot(index='ECC Type', columns='Capacity', values=error_type)
        pivot_data = pivot_data.reindex(index=ecc_types, columns=capacities)
        
        # 히트맵 생성
        sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='YlOrRd', 
                   ax=ax, cbar_kws={'label': f'Number of {error_type}'})
        ax.set_title(f'{error_type} Distribution', fontweight='bold')
        ax.set_xlabel('Memory Capacity')
        ax.set_ylabel('ECC Type')
    
    plt.tight_layout()
    return fig

def create_comparison_chart(df):
    """ECC 효과 비교 차트"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('ECC Effectiveness Comparison', fontsize=16, fontweight='bold')
    
    capacities = sorted(df['Capacity'].unique(), key=parse_capacity)
    
    # 왼쪽: ECC별 총 에러 수 비교
    ax1 = axes[0]
    ecc_types = ['No ECC', 'SECDED', 'ChipKill']
    colors = {'No ECC': 'red', 'SECDED': 'blue', 'ChipKill': 'green'}
    
    for ecc_type in ecc_types:
        data = df[df['ECC Type'] == ecc_type]
        data_sorted = data.set_index('Capacity').reindex(capacities)
        ax1.plot(capacities, data_sorted['Total'], marker='o', linewidth=2, 
                label=ecc_type, color=colors[ecc_type])
    
    ax1.set_title('Total Errors by ECC Type', fontweight='bold')
    ax1.set_xlabel('Memory Capacity')
    ax1.set_ylabel('Total Number of Errors')
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    
    # 오른쪽: ECC별 보호 효과 (No ECC 대비 개선율)
    ax2 = axes[1]
    no_ecc_data = df[df['ECC Type'] == 'No ECC'].set_index('Capacity')
    
    for ecc_type in ['SECDED', 'ChipKill']:
        ecc_data = df[df['ECC Type'] == ecc_type].set_index('Capacity')
        improvement = []
        
        for capacity in capacities:
            no_ecc_total = no_ecc_data.loc[capacity, 'Total']
            ecc_total = ecc_data.loc[capacity, 'Total']
            # 개선율 = (No ECC 에러 - ECC 에러) / No ECC 에러 * 100
            improvement_rate = ((no_ecc_total - ecc_total) / no_ecc_total * 100) if no_ecc_total > 0 else 0
            improvement.append(improvement_rate)
        
        ax2.plot(capacities, improvement, marker='o', linewidth=2, 
                label=f'{ecc_type}', color=colors[ecc_type])
    
    ax2.set_title('Error Reduction Rate vs No ECC (%)', fontweight='bold')
    ax2.set_xlabel('Memory Capacity')
    ax2.set_ylabel('Improvement Rate (%)')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    return fig

def save_statistics_summary(df):
    """통계 요약 저장"""
    summary_file = 'error_statistics_summary.txt'
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("FaultSim Error Statistics Summary\n")
        f.write("="*50 + "\n\n")
        
        # ECC 타입별 평균 통계
        f.write("Average Error Counts by ECC Type:\n")
        f.write("-"*40 + "\n")
        for ecc_type in ['No ECC', 'SECDED', 'ChipKill']:
            data = df[df['ECC Type'] == ecc_type]
            avg_ce = data['CE'].mean()
            avg_ue = data['UE'].mean() 
            avg_sdc = data['SDC'].mean()
            avg_total = data['Total'].mean()
            
            f.write(f"{ecc_type}:\n")
            f.write(f"  Average CE:  {avg_ce:,.1f}\n")
            f.write(f"  Average UE:  {avg_ue:,.1f}\n")
            f.write(f"  Average SDC: {avg_sdc:,.1f}\n")
            f.write(f"  Average Total: {avg_total:,.1f}\n\n")
        
        # 용량별 통계
        f.write("Error Counts by Memory Capacity:\n")
        f.write("-"*40 + "\n")
        capacities = sorted(df['Capacity'].unique(), key=parse_capacity)
        
        for capacity in capacities:
            f.write(f"\n{capacity}:\n")
            data = df[df['Capacity'] == capacity]
            for _, row in data.iterrows():
                f.write(f"  {row['ECC Type']}: CE={row['CE']:,}, UE={row['UE']:,}, SDC={row['SDC']:,}, Total={row['Total']:,}\n")
    
    print(f"Statistics summary saved to: {summary_file}")

def main():
    """메인 함수"""
    csv_file = 'faultsim_error_statistics.csv'
    
    # 데이터 로드
    df = load_and_process_data(csv_file)
    
    # matplotlib 설정
    setup_matplotlib()
    
    # 1. 에러 타입별 서브플롯
    print("Creating error type subplots...")
    fig1 = create_subplot_by_error_type(df)
    fig1.savefig('error_statistics_by_type.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. 스택 바 차트
    print("Creating stacked bar charts...")
    fig2 = create_stacked_bar_chart(df)
    fig2.savefig('error_distribution_stacked.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. 히트맵
    print("Creating heatmaps...")
    fig3 = create_heatmap(df)
    fig3.savefig('error_distribution_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 4. ECC 효과 비교
    print("Creating ECC effectiveness comparison...")
    fig4 = create_comparison_chart(df)
    fig4.savefig('ecc_effectiveness_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 5. 통계 요약 저장
    save_statistics_summary(df)
    
    print("\n" + "="*60)
    print("All visualizations completed!")
    print("Generated files:")
    print("- error_statistics_by_type.png")
    print("- error_distribution_stacked.png") 
    print("- error_distribution_heatmap.png")
    print("- ecc_effectiveness_comparison.png")
    print("- error_statistics_summary.txt")

if __name__ == "__main__":
    main()