// ===== ESLint 扁平配置（合规化计划 W2-3 前端部分） =====
// 定位：前端静态检查，CI 门禁之一（.github/workflows/ci.yml 的 frontend job 执行 `npm run lint`）。
//
// 规则集选择（先量基线再定规则，避免新门禁上线首日即红）：
//   · eslint-plugin-vue 使用 `flat/essential`（防错类）而非 `flat/recommended`——后者含大量排版规则
//     （max-attributes-per-line / html-indent 等），对既有代码会产生数百条格式化告警，属「格式化一次性大改」范畴；
//   · typescript-eslint 使用 @vue/eslint-config-typescript 的默认配置（不做类型感知，保持检查速度）；
//   · skipFormatting 关闭与 Prettier 冲突的规则（Prettier 配置见 .prettierrc.json）。
//
// 后续收紧（见计划 W2-14）：类型感知规则；导入排序仍可继续评估。
// 2026-10-03（批次 193，W2-14 ①）：**已执行 Prettier 一次性格式化**（`npm run format`，175 文件）；
//   `flat/recommended` 的**排版规则明确不引入**——排版归 Prettier，ESLint 只保留防错类（essential），
//   二者混用会互相打架（这正是本配置采用 skip-formatting 的原因）。
import pluginVue from 'eslint-plugin-vue'
import vueTsEslintConfig from '@vue/eslint-config-typescript'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default [
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },
  {
    name: 'app/files-to-ignore',
    ignores: ['**/dist/**', '**/node_modules/**', '**/*.d.ts', '**/coverage/**'],
  },
  ...pluginVue.configs['flat/essential'],
  ...vueTsEslintConfig(),
  skipFormatting,
  {
    name: 'app/rules-deferred',
    rules: {
      // 既有架构债（2026-10-02 实测 10 处，分布于 4 个文件：match-data/SquadCardsGrid.vue、
      // members/MemberTablePanel.vue、members/MemberToolbar.vue、logs/LogFilterBar.vue）：
      // 子组件直接变更 props（query / compareChecked / filters）。
      // 正确修法需改为 emit 更新 + 父组件 v-model，属**行为改动且需浏览器验收**，
      // 故过渡期降为 warn（CI 仍会打印，不会被遗忘），修复任务见合规化计划 W2-8。
      'vue/no-mutating-props': 'warn',
    },
  },
]