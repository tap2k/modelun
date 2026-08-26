# What People Use LLMs For: Taxonomies, Shares, and the Six-Verb Crosswalk

Ecological grounding for the atlas verb set. Collected 2026-08-26 from primary sources;
figure-only numbers flagged. RESIST excluded from coverage (deliberate character probe).

## Sources

1. **OpenAI — "How People Use ChatGPT."** Chatterji, A., Cunningham, T., Deming, D. J.,
   Hitzig, Z., Ong, C., Shan, C. Y., & Wadman, K. (2025). NBER Working Paper No. 34255,
   September 2025. https://www.nber.org/papers/w34255. ~1.1M consumer conversations,
   May 2024–June 2025. 27% work / 73% non-work (June 2025). Topics: Practical Guidance ~29%
   (Tutoring 10.2%, How-To 8.5%), Writing ~24% (modify-provided-text subcats = 2/3 of
   Writing; Edit/Critique largest), Seeking Information ~24%, Multimedia ~7%, Technical Help
   ~5% (Programming 4.2%, Math 3%), Self-Expression ~4–5%. Top three topics ≈ 77% of all
   conversations. Intent: Asking 49 / Doing 40 / Expressing 11.
2. **Anthropic — Clio.** Tamkin, A., McCain, M., Handa, K., et al. (2024). arXiv:2412.13678.
   1M Claude.ai conversations, Oct 2024. Top-10 clusters ≈ 61% of traffic: web/mobile dev
   10.4%, content creation & communication 9.2%, academic research & writing 7.2%, education
   & career 7.1%, AI/ML 6.0%, business strategy 5.7%, translation 4.5%, DevOps 3.9%,
   marketing/SEO 3.7%, data analysis 3.5%. (Figure-derived; verified via secondary
   reporting.) Coding = 15–25% across datasets examined.
3. **Anthropic Economic Index.** Handa, K., Tamkin, A., et al. (2025). arXiv:2503.04761.
   >4M conversations mapped to O*NET. Computer & Mathematical 37.2%; Arts/Design/Media
   10.3%; Education + Science ~15%; augmentation 57% / automation 43%.
4. **WildChat.** Zhao, W., Ren, X., Hessel, J., Cardie, C., Choi, Y., & Deng, Y. (2024).
   ICLR 2024, arXiv:2405.01470. 1M proxy conversations; category shares from 1,000-sample
   first turns: assisting/creative writing 61.9%, analysis/decision explanation 13.6%,
   coding 6.7%, factual info 6.3%, math 6.1%. Caveat: Midjourney-prompt requests inflate
   "creative writing" (per Clio's independent analysis).
5. **Microsoft — Working with AI.** Tomlinson, K., Jaffe, S., Wang, W., Counts, S., &
   Suri, S. (2025). arXiv:2507.07935; data github.com/microsoft/working-with-ai. 200k Bing
   Copilot conversations mapped to O*NET IWAs. Dominant user-goal groupings: learning,
   communicating, teaching/explaining, writing. No in-text shares (repo CSVs only).

## Crosswalk (verb ← source categories)

| Verb | OpenAI | Clio | AEI | WildChat | Microsoft |
|---|---|---|---|---|---|
| EXPLAIN | Seeking Info ~24%; Tutoring 10.2%; How-To 8.5% | education/career 7.1% (part); academic research (part) | Education+Science (~15%, part) | factual info 6.3%; part of analysis 13.6% | gather info; maintain knowledge; teach/explain |
| ADVISE | Health/Self-Care (part of PG ~10%) | business strategy 5.7% (part) | Business/Mgmt (part) | part of analysis 13.6% | advise; provide consultation |
| DRAFT | Personal Writing; Argument/Summary (within Writing 24%) | content creation 9.2% (part); marketing 3.7% (part) | Arts/Media 10.3% (part); Office/Admin (part) | large part of writing 61.9% | write/prepare materials |
| CREATE | Write Fiction; Creative Ideation | content creation (part) | Arts/Media (part) | part of writing 61.9% | develop artistic content |
| EDIT | Edit/Critique (largest Writing subcat; modify-text = 2/3 of Writing) | content/academic writing (part) | writing tasks (part) | part of writing ("assisting") | edit written materials |
| INTERPRET | Data Analysis 0.4%; Analyze Image (part); part of Argument/Summary | data analysis 3.5% (part) | analyst occupations (part) | part of analysis 13.6% | interpret info; analyze data |
| NONE | Programming 4.2%; Math 3%; image-gen (~7 Multimedia); Translation ~4–5%; Self-Expression ~4–5% | coding ~20.3pp of top-10; translation 4.5% | Computer & Math 37.2% | coding 6.7%; math 6.1%; Midjourney/roleplay mass | operate computers; misc small |

## Coverage estimates (six verbs)

- **OpenAI (cleanest fit): ~72–74% of all consumer usage; ~76–78% of non-coding usage.**
- **WildChat:** nominally ~88% of non-coding; realistically ~65–80% after discounting
  Midjourney-prompt/roleplay mass inside "creative writing."
- **Clio:** ~90–95% of the non-coding, non-translation top-10 mass, but 39% long tail
  unmapped → defensible claim: "roughly half of non-coding Claude.ai usage, wide uncertainty."
- **AEI:** ~70–85% of non-coding mapped usage (loosest — units are O*NET tasks).
- **Microsoft:** qualitatively very high (dominant groupings all inside the verbs); no
  printed shares.

**Headline sentence:** the six usage verbs cover roughly three-quarters of consumer ChatGPT
usage (Chatterji et al. 2025) and the majority of non-coding usage in every major usage
study; principal exclusions are coding, image generation, translation, and
roleplay/companionship — each excluded deliberately (capability-benchmarked, out of modality,
out of scope for an advisor-character atlas).

## Uncertainties

Units differ (messages / conversations / first turns / IWA mentions); populations differ
(consumer ChatGPT vs coding-heavy Claude.ai vs proxy users vs Copilot-at-work); ambiguous
mappings (Argument/Summary straddles DRAFT/INTERPRET/EDIT; How-To straddles EXPLAIN/ADVISE;
Clio's content-creation cluster mixes DRAFT/CREATE/EDIT); Clio and OpenAI granular numbers
are figure-derived; translation share in OpenAI inferred from subcategory ordering, not
printed.
