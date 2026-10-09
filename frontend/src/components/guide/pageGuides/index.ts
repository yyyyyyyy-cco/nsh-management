/** 页面详解分组汇总（内容按域分文件维护，改文案不动组件）。 */
import type { GuidePageGroup } from '../guideContent'

import { analyticsGroup } from './analytics'
import { homeSystemGroup } from './homeSystem'
import { operationsGroup } from './operations'
import { peopleGroup } from './people'

export const GUIDE_PAGE_GROUPS: GuidePageGroup[] = [operationsGroup, analyticsGroup, peopleGroup, homeSystemGroup]
