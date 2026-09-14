# TODO

## In Progress

(Nothing currently in progress.)

## Done

- [x] 2026-09-13 — v1.3.0 — security hardening round two: rate
      limiting, field validation, CORS wildcard guard, safer defaults,
      hardened dependency guards, frontend error states, and pinned
      npm dependency ranges (#security, #frontend)
- [x] 2026-09-13 — v1.2.0 — security hardening and public-release prep:
      zero-vulnerability dependency upgrades, pinned model revision,
      security headers, docs toggle, CI audits and supply-chain
      hardening (#security, #infra, #docs)
- [x] 2026-09-05 — v1.1.0 — repository hardening: expanded backend and
      frontend test suites (coverage gates, `--runmodel` gate, lazy
      PyTorch imports), corrected CI pipeline, expanded README and
      security policy, and dependency-update automation (#test, #docs,
      #infra)
- [x] 2026-08-25 — v1.0.0 — Initial implementation: backend, frontend,
      model integration, explanation, tests, docs, CI (#backend,
      #frontend, #model, #test, #docs, #infra)

## High Priority

(Important changes that should be done soon.)

- [ ] Add E2E tests with Playwright covering the full analyze flow (#test)

## Medium Priority

(Should get done, not urgent.)

- [ ] Test Captum attribution against known phrase-level expectations
      (#test, #model)
- [ ] Investigate ONNX Runtime + quantized model for faster inference
      (#performance)
- [ ] Add character/word count to the SentenceAnalysis response (#api)

## Low Priority

(Nice-to-haves.)

- [ ] Add reduced-motion media query support to animations (#frontend)
- [ ] Add axe-core accessibility tests to CI (#accessibility, #test)

## Ideas

(Interesting ideas not yet committed to implementation.)

- [ ] Radial bubble visualization as an alternative to the bar chart
      (#frontend)
- [ ] User-configurable emotion threshold in the UI (#frontend)
