"""
Interactive Visualization Dashboard
Generates visual reports and charts for allocation decisions
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List
from charity_decision_system import FundAllocationResult, AllocationDecision


class AllocationVisualizer:
    """Creates visualizations for fund allocation results"""
    
    def __init__(self):
        self.colors = {
            'fully_funded': '#2ecc71',
            'partially_funded': '#f39c12',
            'rejected': '#e74c3c',
            'primary': '#3498db',
            'secondary': '#9b59b6'
        }
    
    def plot_allocation_overview(self, result: FundAllocationResult, title: str = "Fund Allocation Overview"):
        """Create a comprehensive overview dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # 1. Budget utilization pie chart
        self._plot_budget_utilization(ax1, result)
        
        # 2. Decisions breakdown
        self._plot_decisions_breakdown(ax2, result)
        
        # 3. Top funded programs
        self._plot_top_programs(ax3, result)
        
        # 4. Efficiency vs Impact scatter
        self._plot_efficiency_impact(ax4, result)
        
        plt.tight_layout()
        return fig
    
    def _plot_budget_utilization(self, ax, result: FundAllocationResult):
        """Pie chart showing budget allocation vs remaining"""
        sizes = [result.total_allocated, result.remaining_budget]
        labels = [f'Allocated\n${result.total_allocated:,.0f}', 
                 f'Remaining\n${result.remaining_budget:,.0f}']
        colors = [self.colors['primary'], '#ecf0f1']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors, startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Budget Utilization', fontweight='bold')
    
    def _plot_decisions_breakdown(self, ax, result: FundAllocationResult):
        """Bar chart showing decision breakdown"""
        categories = ['Fully\nFunded', 'Partially\nFunded', 'Rejected']
        values = [result.num_fully_funded, result.num_partially_funded, result.num_rejected]
        colors = [self.colors['fully_funded'], 
                 self.colors['partially_funded'], 
                 self.colors['rejected']]
        
        bars = ax.bar(categories, values, color=colors, alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Number of Requests', fontweight='bold')
        ax.set_title('Decision Breakdown', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_top_programs(self, ax, result: FundAllocationResult):
        """Horizontal bar chart of top funded programs"""
        # Get funded programs sorted by amount
        funded = [d for d in result.decisions if d.amount_allocated > 0]
        funded.sort(key=lambda d: d.amount_allocated, reverse=True)
        
        # Take top 5
        top_n = min(5, len(funded))
        top_funded = funded[:top_n]
        
        program_names = [d.request.program_name[:30] for d in top_funded]
        amounts = [d.amount_allocated / 1000 for d in top_funded]  # In thousands
        
        # Color by funding status
        colors = [self.colors['fully_funded'] if d.is_fully_funded() 
                 else self.colors['partially_funded'] for d in top_funded]
        
        y_pos = np.arange(len(program_names))
        bars = ax.barh(y_pos, amounts, color=colors, alpha=0.8)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(program_names)
        ax.invert_yaxis()
        ax.set_xlabel('Amount Allocated ($1000s)', fontweight='bold')
        ax.set_title('Top Funded Programs', fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'${amounts[i]:.0f}k',
                   ha='left', va='center', fontweight='bold')
    
    def _plot_efficiency_impact(self, ax, result: FundAllocationResult):
        """Scatter plot of efficiency vs people benefitted"""
        funded = [d for d in result.decisions if d.amount_allocated > 0]
        
        if not funded:
            ax.text(0.5, 0.5, 'No funded programs', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        x = [d.request.efficiency_ratio() * 100 for d in funded]
        y = [d.request.people_benefitted * d.allocation_percentage for d in funded]
        sizes = [d.amount_allocated / 1000 for d in funded]  # Bubble size
        
        colors_list = [self.colors['fully_funded'] if d.is_fully_funded() 
                      else self.colors['partially_funded'] for d in funded]
        
        scatter = ax.scatter(x, y, s=sizes, c=colors_list, alpha=0.6, edgecolors='black')
        
        ax.set_xlabel('Efficiency (%)', fontweight='bold')
        ax.set_ylabel('People Benefitted', fontweight='bold')
        ax.set_title('Efficiency vs Impact (bubble size = $ allocated)', fontweight='bold')
        ax.grid(alpha=0.3)
        
        # Add program labels for top 3
        top_3 = sorted(funded, key=lambda d: d.request.people_benefitted, reverse=True)[:3]
        for d in top_3:
            idx = funded.index(d)
            ax.annotate(d.request.program_name[:20], 
                       (x[idx], y[idx]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.7)
    
    def plot_ranking_comparison(self, result: FundAllocationResult):
        """Compare priority scores with allocation decisions"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by rank
        sorted_decisions = sorted(result.decisions, key=lambda d: d.rank)
        
        ranks = [d.rank for d in sorted_decisions]
        scores = [d.priority_score for d in sorted_decisions]
        allocations = [d.allocation_percentage * 100 for d in sorted_decisions]
        
        # Create bar chart
        x = np.arange(len(ranks))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, scores, width, label='Priority Score', 
                      color=self.colors['primary'], alpha=0.8)
        bars2 = ax.bar(x + width/2, [a/100 for a in allocations], width, 
                      label='Allocation %', alpha=0.8)
        
        # Color bars2 by funding status
        for i, (bar, d) in enumerate(zip(bars2, sorted_decisions)):
            if d.is_fully_funded():
                bar.set_color(self.colors['fully_funded'])
            elif d.is_partially_funded():
                bar.set_color(self.colors['partially_funded'])
            else:
                bar.set_color(self.colors['rejected'])
        
        ax.set_xlabel('Rank', fontweight='bold')
        ax.set_ylabel('Score / Percentage', fontweight='bold')
        ax.set_title('Priority Ranking vs Allocation Decision', fontweight='bold', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels([f'#{r}' for r in ranks])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_strategy_comparison(self, results_dict: dict):
        """Compare multiple allocation strategies"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Strategy Comparison', fontsize=16, fontweight='bold')
        
        strategies = list(results_dict.keys())
        
        # 1. Utilization rates
        utilization = [r.utilization_rate() for r in results_dict.values()]
        bars = ax1.bar(strategies, utilization, color=self.colors['primary'], alpha=0.8)
        ax1.set_ylabel('Utilization Rate (%)', fontweight='bold')
        ax1.set_title('Budget Utilization by Strategy', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        for bar, val in zip(bars, utilization):
            ax1.text(bar.get_x() + bar.get_width()/2., val,
                    f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 2. People benefitted
        people = [r.total_people_benefitted for r in results_dict.values()]
        bars = ax2.bar(strategies, people, color=self.colors['secondary'], alpha=0.8)
        ax2.set_ylabel('People Benefitted', fontweight='bold')
        ax2.set_title('Total People Benefitted', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        for bar, val in zip(bars, people):
            ax2.text(bar.get_x() + bar.get_width()/2., val,
                    f'{val:,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # 3. Decision breakdown
        x = np.arange(len(strategies))
        width = 0.25
        
        fully = [r.num_fully_funded for r in results_dict.values()]
        partial = [r.num_partially_funded for r in results_dict.values()]
        rejected = [r.num_rejected for r in results_dict.values()]
        
        ax3.bar(x - width, fully, width, label='Fully Funded', 
               color=self.colors['fully_funded'], alpha=0.8)
        ax3.bar(x, partial, width, label='Partially Funded', 
               color=self.colors['partially_funded'], alpha=0.8)
        ax3.bar(x + width, rejected, width, label='Rejected', 
               color=self.colors['rejected'], alpha=0.8)
        
        ax3.set_ylabel('Number of Requests', fontweight='bold')
        ax3.set_title('Decision Breakdown', fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(strategies)
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Average efficiency
        efficiency = [r.average_efficiency_ratio * 100 for r in results_dict.values()]
        bars = ax4.bar(strategies, efficiency, color='#16a085', alpha=0.8)
        ax4.set_ylabel('Average Efficiency (%)', fontweight='bold')
        ax4.set_title('Average Efficiency Ratio', fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        for bar, val in zip(bars, efficiency):
            ax4.text(bar.get_x() + bar.get_width()/2., val,
                    f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def save_report(self, result: FundAllocationResult, filename: str = "allocation_report.png"):
        """Save allocation overview to file"""
        fig = self.plot_allocation_overview(result)
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return filename


def create_visual_report(result: FundAllocationResult, strategy_name: str = "Allocation"):
    """Generate and display visual report"""
    viz = AllocationVisualizer()
    
    # Create overview dashboard
    fig1 = viz.plot_allocation_overview(result, f"{strategy_name} - Overview")
    
    # Create ranking comparison
    fig2 = viz.plot_ranking_comparison(result)
    
    plt.show()
    
    return viz


if __name__ == "__main__":
    # Example usage
    from example_usage import create_sample_requests
    from fund_allocator import FundAllocator
    
    requests = create_sample_requests()
    allocator = FundAllocator(total_budget=500000)
    result = allocator.allocate_greedy(requests, allow_partial=True)
    
    viz = AllocationVisualizer()
    viz.plot_allocation_overview(result)
    plt.show()
