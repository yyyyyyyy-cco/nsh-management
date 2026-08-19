/** ECharts 浅色雅金风主题（对齐 ui-style-guide）。 */

export const CHART_THEME = {
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.96)',
    borderColor: '#e6d9b3',
    borderWidth: 1,
    padding: [10, 14],
    textStyle: { color: '#4a4238', fontSize: 13 },
    extraCssText: 'backdrop-filter: blur(8px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); border-radius: 8px;',
  },
  legend: { textStyle: { color: '#7a7368', fontSize: 12 }, itemGap: 16 },
  axis: {
    axisLabel: { color: '#8a8378', fontSize: 12 },
    axisName: { color: '#6d665c', fontSize: 13, fontWeight: 500 },
    splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)', type: 'dashed' } },
  },
}
