"""
animations.py — Animation utilities for dynamic KPI cards
Provides advanced animations: count-up, glow, shimmer, hover lift, staggered appearance
"""

def kpi_card_animated(label: str, value: str, subtitle: str, color: str = "orange", card_index: int = 0) -> str:
    """
    Enhanced KPI card with multiple animation effects:
    - Count-up effect on numbers
    - Top border glow animation
    - Hover lift effect
    - Shimmer effect on load
    - Staggered appearance
    
    Args:
        label: Card label
        value: The value to animate (e.g., "₹48.3M", "1,234")
        subtitle: Subtext below value
        color: Color theme (orange, blue, purple, red, green)
        card_index: Position (0, 1, 2, 3...) for staggered timing
    
    Returns:
        HTML string with advanced animated KPI card
    """
    card_id = f"kpi-{label.replace(' ', '-').lower()}"
    stagger_delay = card_index * 150  # 150ms stagger between cards
    
    return f"""
    <div class="kpi-card c-{color} kpi-enhanced" id="card-{card_id}" style="--stagger-delay: {stagger_delay}ms;">
      <div class="kpi-glow-effect"></div>
      <div class="kc-label">{label}</div>
      <div class="kc-val kpi-count-up" id="{card_id}" data-value="{value}">
        <span class="count-text">0</span>
      </div>
      <div class="kc-sub">{subtitle}</div>
    </div>
    <script>
      (function() {{
        const cardContainer = document.getElementById('card-{card_id}');
        const element = document.getElementById('{card_id}');
        if (!element || !cardContainer) return;
        
        const targetValue = element.getAttribute('data-value');
        const countSpan = element.querySelector('.count-text');
        if (!countSpan) return;
        
        // Count-up animation: extract numeric part and animate
        function extractNumber(str) {{
          const match = str.match(/\\d+(?:\\.\\d+)?/);
          return match ? parseFloat(match[0]) : 0;
        }}
        
        function formatNumber(num, original) {{
          // Reconstruct formatted number with prefix/suffix
          const numStr = Math.round(num).toString();
          let result = original;
          const origNum = result.match(/\\d+(?:\\.\\d+)?/);
          if (origNum) {{
            result = result.replace(origNum[0], numStr);
          }}
          return result;
        }}
        
        const numValue = extractNumber(targetValue);
        const startDelay = {stagger_delay};
        
        // Start count-up after stagger delay
        setTimeout(() => {{
          const duration = 1200; // 1.2 seconds for count-up
          const startTime = Date.now();
          
          function updateCount() {{
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function: cubic out
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const currentNum = numValue * easeProgress;
            
            countSpan.textContent = formatNumber(currentNum, targetValue);
            
            if (progress < 1) {{
              requestAnimationFrame(updateCount);
            }} else {{
              // Final value
              countSpan.textContent = targetValue;
            }}
          }}
          
          updateCount();
        }}, startDelay);
      }})();
    </script>
    """


def animated_plotly_config():
    """
    Plotly config for animations on charts.
    Returns dict of animation settings for use in st.plotly_chart config.
    """
    return {
        "responsive": True,
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {
            "format": "png",
            "filename": "chart",
            "height": 600,
            "width": 1200,
            "scale": 2,
        },
    }
