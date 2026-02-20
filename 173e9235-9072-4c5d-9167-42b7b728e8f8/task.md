# Archive Cleanup Task

- [x] List contents of the `archive` folder on the Desktop
- [x] Compare `archive` contents against `AG-PROJECTS-mac-` repository
  - *Result*: The `archive` folder contains the **actual source code** (e.g., `AutoPlotDigitizerWeb`). It is **NOT** backed up in Git or GitHub yet.
- [x] Ensure any missing projects/files are migrated to `AG-PROJECTS-mac-` (User confirmed option 1)
- [x] Delete files in `archive` that are safely backed up in Git/GitHub
  - *Result*: Moved `AutoPlotDigitizerWeb`, `AutoPlotDigitizerV1_Windows_Port`, and `AutoPlotDigitizerV2_Windows_Port` to `AG-PROJECTS-mac-`. Deleted the rest of the loose `archive` directory files. Committed and pushed to GitHub.

# Project Restructuring Task
- [x] Create `Project1-AutoPlotDigitizer` and `Project2-FitnessApp` directories
- [x] Move corresponding directories into the project folders via `git mv`
- [x] Commit and push the structural changes
