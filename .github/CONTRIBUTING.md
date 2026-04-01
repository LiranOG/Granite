# Contributing to GRANITE

Thank you for your interest in contributing to GRANITE! This document provides
guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** and clone your fork locally.
2. **Set up your development environment** — see `docs/developer_guide/setup.rst`.
3. **Create a feature branch** from `develop`: `git checkout -b feature/your-feature develop`
4. **Build and test** before submitting: `mkdir build && cd build && cmake .. && make -j && ctest`

## Development Workflow

### Branch Model

- `main` — stable releases only (tagged with semantic versioning)
- `develop` — integration branch for next release
- `feature/*` — individual feature branches
- `bugfix/*` — bug fixes
- `release/*` — release preparation

### Code Standards

- **Language**: C++17 for core code; CUDA/HIP for GPU kernels; Python 3.10+ for analysis
- **Style**: Follow the `.clang-format` configuration (LLVM-based, 100 char line width)
- **Naming**:
  - Classes: `PascalCase` (e.g., `CCZ4Evolution`)
  - Functions: `camelCase` (e.g., `computeRHS`)
  - Variables: `snake_case` (e.g., `conformal_factor`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_REFINEMENT_LEVELS`)
  - Namespaces: `lowercase` (e.g., `granite::spacetime`)
- **Documentation**: All public APIs must have Doxygen comments

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat(ccz4): implement Kreiss-Oliger dissipation operator
fix(grmhd): correct con2prim fallback in magnetically dominated cells
test(amr): add boundary reflection coefficient test
docs(user-guide): add tutorial for binary BH setup
perf(riemann): optimize HLLD solver inner loop
```

### Pull Request Process

1. Ensure all tests pass (`ctest --output-on-failure`)
2. Add tests for new functionality
3. Update documentation if APIs change
4. Request review from at least **one core developer**
5. Squash merge into `develop` after approval

## Testing

### Running Tests

```bash
cd build
ctest --output-on-failure          # All tests
ctest -R spacetime                  # Spacetime module only
ctest -R convergence --timeout 600  # Convergence tests (longer)
```

### Writing Tests

- Place tests in `tests/<module>/` mirroring `src/<module>/`
- Use GoogleTest framework
- Name test files `test_<feature>.cpp`
- Each test should complete in < 60 seconds (unit) or < 600 seconds (convergence)

## Reporting Issues

Use GitHub Issues with the following labels:
- `bug` — something doesn't work correctly
- `enhancement` — feature request
- `physics` — question about the physics implementation
- `performance` — performance concern
- `documentation` — documentation improvement

## Code Review Checklist

Reviewers should verify:
- [ ] Code compiles without warnings (`-Wall -Wextra -Wpedantic`)
- [ ] All existing tests pass
- [ ] New tests cover the changed code
- [ ] Physics implementation matches equations in the theory manual
- [ ] No hardcoded magic numbers (use named constants)
- [ ] Memory management is correct (no leaks, RAII)
- [ ] GPU kernels have correct thread/block configuration
- [ ] Documentation is updated
