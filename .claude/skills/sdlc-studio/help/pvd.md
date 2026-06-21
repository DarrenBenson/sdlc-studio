# Help: pvd

The **Product Vision Document** - the product layer above the PRD, coordinating the repos
that form one product. Opt-in: a single repo never needs it.

## Commands

```bash
/sdlc-studio pvd create      # render the tiered master PVD into the product repo
/sdlc-studio pvd sync        # project the master read-only into each child repo (CR0048)
/sdlc-studio product reconcile   # verify the feature map + contracts across repos (CR0049)
```

## What it is

- One writable master at `sdlc-studio/product/pvd.md` (Product Manager owns it), child repos
  get it read-only.
- `sdlc-studio/product/manifest.yaml` lists the child repos (id / path / url).
- Coordinates and traces (feature -> owning repo -> PRD feature), never re-specifies.
- **Lean by default**; the topology tree, G1-G5 gates, and release coordination are opt-in
  for large multi-team products - delete them if unused.

## See also

- `reference-pvd.md` - the workflow
- `templates/core/pvd.md`, `templates/product-manifest.yaml`
- RFC0015 - the design (accepted, scoped WS1-3)
