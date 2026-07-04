# Help: pvd

<!-- Load when: /sdlc-studio pvd - the Product Vision Document multi-repo layer -->

The **Product Vision Document** - the product layer above the PRD, coordinating the repos
that form one product. Opt-in: a single repo never needs it.

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Set up a product vision across our repos" | `/sdlc-studio pvd create` |
| "Push the vision out to each child repo" | `/sdlc-studio pvd sync` |
| "Has a child repo's projection gone stale?" | `/sdlc-studio pvd drift` |

## Commands

```bash
/sdlc-studio pvd create      # render the tiered master PVD into the product repo
/sdlc-studio pvd sync        # project the master read-only into each child repo
/sdlc-studio pvd drift       # fail loud if a child projection has gone stale
```

## What it is

- One writable master at `sdlc-studio/product/pvd.md` (Product Manager owns it), child repos
  get it read-only.
- `sdlc-studio/product/manifest.yaml` lists the child repos (id / path / url).
- Coordinates and traces (feature -> owning repo -> its CR/RFC/PRD artefact), never re-specifies.
- **Lean by default**; the topology tree, G1-G5 gates, and release coordination are opt-in
  for large multi-team products - delete them if unused.

## See also

- `reference-pvd.md` - the workflow
- `templates/core/pvd.md`, `templates/product-manifest.yaml`
- the design rationale (accepted)
