# Harness Checklist

## Before implementation
- [ ] Record both repository SHAs
- [ ] Run source baseline
- [ ] Run target baseline
- [ ] Inventory every source package/component/flow
- [ ] Initialize parity matrix
- [ ] Write/update SDD for first slice

## Per language/runtime change
- [ ] Failing/characterization test exists
- [ ] Parser/AST coverage exists if syntax changed
- [ ] Invalid syntax coverage exists
- [ ] Renderer/runtime coverage exists
- [ ] Existing demos still parse/run
- [ ] `cargo test` green
- [ ] LANGUAGE.md updated only after verified

## Per component
- [ ] Source implementation inspected
- [ ] Variants inventoried
- [ ] States inventoried
- [ ] A11y behavior inventoried
- [ ] Tokens/theme dependencies inventoried
- [ ] Target contract written
- [ ] Functional tests green
- [ ] Keyboard tests green where interactive
- [ ] Theme tests green
- [ ] RTL/i18n checked
- [ ] Visual evidence stored
- [ ] Parity row = VERIFIED

## Final
- [ ] All parity rows accounted for
- [ ] No hidden React/Node runtime dependency
- [ ] Docs examples executable
- [ ] CLI/scaffolds tested
- [ ] Performance measured
- [ ] Final report generated
