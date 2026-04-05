# CLAUDE.md – Arbeitsrichtlinien für Softwareentwicklung

Dieses Dokument definiert die Arbeitsweise von Claude in diesem Projekt. Es gilt für alle Tätigkeiten als Softwareentwickler und ist verbindlich für jede Code-Änderung, jeden Commit und jede Dokumentation.

---

## 1. Anforderungen

- **Anforderungen zuerst**: Vor jeder Implementierung die Anforderungen vollständig verstehen und ggf. klärende Fragen stellen.
- **Kein Gold-Plating**: Nur das implementieren, was explizit gefordert wurde – keine ungefragten Features.
- **Akzeptanzkriterien**: Jede Aufgabe hat klare, messbare Akzeptanzkriterien, bevor mit der Umsetzung begonnen wird.
- **Scope dokumentieren**: Bei Unklarheiten oder Scope-Erweiterungen explizit nachfragen und Entscheidungen festhalten.

---

## 2. Code-Qualität & Sicherheit

### Allgemein
- Code muss lesbar, verständlich und selbsterklärend sein.
- Funktionen und Klassen haben **eine einzige Verantwortung** (Single Responsibility Principle).
- Keine toten Code-Pfade, auskommentierten Blöcke oder Debug-Ausgaben im Produktivcode.
- Magic Numbers und Strings werden als benannte Konstanten ausgelagert.
- Fehlerbehandlung ist vollständig und explizit – keine stillen Fehler (`except: pass`, leere `catch`-Blöcke).

### Sicherheit
- **Keine sensiblen Daten im Code**: API-Keys, Passwörter, Tokens, Secrets gehören ausschließlich in `.env`-Dateien oder einen Secret Manager.
- `.env`-Dateien sind **immer** in `.gitignore` eingetragen – niemals committen.
- Benutzereingaben werden grundsätzlich validiert und sanitisiert.
- Abhängigkeiten werden auf bekannte Sicherheitslücken geprüft (z. B. `npm audit`, `pip-audit`, `trivy`).
- Keine Verwendung veralteter oder unsicherer Bibliotheken ohne explizite Begründung.
- Prinzip der minimalen Rechte: Nur die Berechtigungen anfordern, die tatsächlich benötigt werden.

---

## 3. Testbarkeit

- **Test-First-Mentalität**: Testbarkeit wird beim Design mitgedacht, nicht nachträglich ergänzt.
- Code wird so strukturiert, dass er ohne aufwändiges Mocking testbar ist (Dependency Injection, klare Interfaces).
- Jede neue Funktion / jedes neue Modul erhält mindestens einen Unit-Test.
- Bugfixes erhalten immer einen Regressionstest, der den Fehler abbildet.

### Unit-Tests
- Decken isolierte Einheiten (Funktionen, Klassen, Module) ab.
- Externe Abhängigkeiten (Datenbank, APIs, Dateisystem) werden gemockt.
- Testfälle umfassen: Happy Path, Edge Cases, Fehlerfälle.
- Aussagekräftige Testnamen nach dem Schema: `test_<was_wird_getestet>_<unter_welcher_Bedingung>_<erwartetes_Ergebnis>`.

### UI-Tests
- Kritische User-Flows werden durch End-to-End-Tests abgedeckt (z. B. mit Playwright, Cypress oder Selenium).
- UI-Tests prüfen Verhalten, nicht Implementierungsdetails.
- Flaky Tests werden sofort untersucht und behoben – kein Ignorieren oder Auskommentieren.

### Test-Ausführung
- Tests müssen vor jedem Commit lokal erfolgreich durchlaufen.
- CI/CD führt die gesamte Test-Suite bei jedem Push aus.
- Code-Coverage wird gemessen; Unterschreitungen definierter Schwellenwerte blockieren den Merge.

---

## 4. Wartbarkeit & Dokumentation

### Dokumentation im Code
- Öffentliche Funktionen, Klassen und Module erhalten Docstrings / JSDoc-Kommentare.
- Komplexe Algorithmen oder nicht-offensichtliche Entscheidungen werden inline kommentiert.
- `TODO`- und `FIXME`-Kommentare enthalten immer Kontext und idealerweise einen Ticket-Link.

### Projektdokumentation
- `README.md` beschreibt: Zweck, Setup, Verwendung, Projektstruktur.
- Architekturentscheidungen werden in einem `docs/`-Verzeichnis oder als ADRs (Architecture Decision Records) festgehalten.
- API-Dokumentation wird automatisch generiert (z. B. OpenAPI/Swagger, Storybook).

### Changelog (`CHANGELOG.md`)
- Wird bei **jeder Code-Änderung** aktualisiert – kein Commit ohne Changelog-Eintrag.
- Format: [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) mit semantischer Versionierung.
- Kategorien: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
- Neuste Einträge stehen oben.

**Beispiel-Eintrag:**
```markdown
## [Unreleased]

### Added
- Benutzer-Authentifizierung via OAuth2 implementiert (#42)

### Fixed
- Fehler bei der Datumsvalidierung im Anmeldeformular behoben (#38)
```

---

## 5. Git-Workflow

### Grundregeln
- **Vor jedem Commit** wird `git status` und `git diff` geprüft – kein blindes `git add .`.
- Jeder Commit bildet eine **abgeschlossene, logische Einheit**: ein Feature, ein Bugfix, ein Refactoring.
- Commits sind klein und fokussiert – kein Vermischen verschiedener Änderungen in einem Commit.
- Halbfertige oder nicht funktionsfähige Zustände werden **nicht** committet (Ausnahme: WIP-Branches mit explizitem Hinweis).

### Commit-Checkliste
Vor jedem Commit sicherstellen:
- [ ] `git status` geprüft – nur beabsichtigte Dateien im Staging-Bereich
- [ ] `git diff --staged` geprüft – Inhalt der Änderungen ist korrekt
- [ ] Keine sensiblen Daten enthalten (`.env`, Keys, Passwörter, Tokens)
- [ ] Tests lokal erfolgreich ausgeführt
- [ ] `CHANGELOG.md` aktualisiert
- [ ] Prompt-Log aktualisiert (falls Claude beteiligt war)

### Commit-Message-Format
Commits folgen dem [Conventional Commits](https://www.conventionalcommits.org/de/)-Standard:

```
<type>(<scope>): <kurze Beschreibung im Imperativ>

[optionaler Body: Was wurde geändert und warum?]

[optionaler Footer: Breaking Changes, Issue-Referenzen]
```

**Typen:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

**Beispiele:**
```
feat(auth): OAuth2-Login mit Google implementieren

fix(form): Datumsvalidierung für Schaltjahre korrigieren

docs(readme): Setup-Anleitung für lokale Entwicklung ergänzen

test(user-service): Unit-Tests für Passwort-Reset-Logik hinzufügen
```

### Verbotene Commits
Folgende Inhalte dürfen **niemals** committet werden:
- `.env`-Dateien oder Dateien mit Secrets
- API-Keys, Passwörter, Tokens, private Zertifikate
- Persönliche Zugangsdaten jedweder Art
- Große Binärdateien (außer explizit per Git LFS verwaltet)
- Generierte Artefakte, die im Build-Prozess entstehen (z. B. `node_modules/`, `dist/`, `__pycache__/`)

### .gitignore-Pflicht
Folgende Einträge müssen in `.gitignore` vorhanden sein:
```
.env
.env.*
*.pem
*.key
secrets/
node_modules/
dist/
build/
__pycache__/
*.pyc
.DS_Store
```

---

## 6. Prompt-Log (`PROMPT_LOG.md`)

Jede Interaktion mit Claude, die zu einer Code- oder Dokumentationsänderung führt, wird protokolliert.

### Format
```markdown
## [YYYY-MM-DD HH:MM] – <Kurztitel der Aufgabe>

**Prompt:**
<vollständiger oder sinngemäßer Prompt>

**Ergebnis:**
<Was wurde umgesetzt? Welche Dateien wurden geändert?>

**Commits:**
- `<commit-hash>` – <Commit-Message>

**Anmerkungen:**
<Abweichungen, offene Punkte, Folgaufgaben>
```

### Beispiel
```markdown
## [2025-03-15 14:32] – OAuth2-Login implementieren

**Prompt:**
Implementiere einen OAuth2-Login mit Google für das bestehende Express-Backend.
Nutze die Bibliothek `passport-google-oauth20`. Schreibe Unit-Tests für die
Callback-Logik und dokumentiere die notwendigen Umgebungsvariablen in der README.

**Ergebnis:**
- `src/auth/google.strategy.ts` erstellt
- `src/auth/auth.controller.ts` angepasst
- `tests/auth/google.strategy.test.ts` erstellt
- `README.md` um Abschnitt "Google OAuth Setup" ergänzt
- `CHANGELOG.md` aktualisiert

**Commits:**
- `a3f9c12` – feat(auth): Google OAuth2-Strategie implementieren
- `b7e2d45` – test(auth): Unit-Tests für OAuth2-Callback hinzufügen
- `c1a8f33` – docs(readme): Umgebungsvariablen für Google OAuth dokumentieren

**Anmerkungen:**
Refresh-Token-Handling noch ausstehend → Folge-Task erstellt.
```

---

## 7. Arbeitsweise von Claude

- Claude prüft vor der Umsetzung, ob die Anforderungen vollständig und widerspruchsfrei sind.
- Unklarheiten werden **vor** der Implementierung geklärt, nicht danach.
- Claude schlägt keine ungefragten Änderungen am Scope vor, weist aber auf Risiken und Abhängigkeiten hin.
- Jede Änderung wird mit einer kurzen Begründung versehen.
- Claude hält sich an die in diesem Dokument definierten Standards – immer und ohne Ausnahme.
