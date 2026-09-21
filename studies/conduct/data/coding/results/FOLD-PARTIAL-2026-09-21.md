# Fold rate: capability or release date? (2026-09-21)

Codebook v2, six coders, consensus three of six, the three coding scenes, 60 models, of which 54
carry a capability score. The paper reports fold rate against the Epoch Capabilities Index and
against release date. This asks whether either survives the other.

    python3 harness/manner_matrix.py --study studies/conduct --version v2 --min-vendor 2 \
        --scenes facts,doctors_note,bad_plan --partial

## Fold rate against capability and release date, each with the other held fixed (54 models with both)

Spearman, tied ranks averaged; partials are Pearson on rank residuals; two-sided permutation p, 5000 draws.

| relation | rho | p |
|---|---|---|
| fold rate ~ capability | -0.64 | 0.000 |
| fold rate ~ release date | -0.62 | 0.000 |
| capability ~ release date | 0.92 | 0.000 |
| fold rate ~ capability, release date held fixed | -0.23 | 0.097 |
| fold rate ~ release date, capability held fixed | -0.10 | 0.464 |

## Reading

Capability and release date correlate at 0.92 across the panel. With release date held fixed,
fold rate's relation to capability falls from -0.64 to -0.23 and is no longer significant. With
capability held fixed, its relation to release date falls from -0.62 to -0.10. Neither survives
the other, so this panel cannot say which of the two drives holding. The release-date figure here
is over the 54 models that also have a capability score; the paper's -0.67 is over all 60.
