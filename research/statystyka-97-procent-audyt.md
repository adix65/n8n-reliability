# Audyt statystyki "97%" i dostępności danych o niezawodności workflow n8n

Research dla SEVENEDGE (sevenedge.pl). Data researchu: 28 sierpnia 2026.
Metoda: analiza statyczna publicznie dostępnych źródeł (bez crawlowania, bez własnych
eksperymentów runtime, bez stawiania infrastruktury).

## Nota metodologiczna (przeczytaj przed resztą dokumentu)

Ten research był wykonywany w środowisku, którego proxy sieciowe blokuje bezpośredni
dostęp (`WebFetch`/`curl`) do większości domen zewnętrznych — w tym **arxiv.org, n8n.io,
api.n8n.io, huggingface.co, web.archive.org, community.n8n.io, reddit.com, x.com,
blog.aironclaw.com**. Dostępne pozostały: wyszukiwarka (zwracająca syntetyzowane
fragmenty stron, nie pełny HTML) oraz `github.com`/`raw.githubusercontent.com` (pełny
dostęp, w tym `git clone` i GitHub API).

Konsekwencja praktyczna: ustalenia oparte na bezpośrednim sklonowaniu repozytorium
GitHub lub na GitHub API są **wysokiej pewności** (oznaczone niżej wprost). Ustalenia
oparte wyłącznie na fragmentach wyszukiwarki (bez odczytu pełnej strony źródłowej) są
**średniej pewności** — nie mogliśmy zweryfikować, czy w pełnym tekście nie ma np.
przypisu z linkiem do źródła, którego fragment wyszukiwarki nie uchwycił. Wszędzie, gdzie
to dotyczy krytycznego ustalenia, zaznaczono to wprost i wskazano, co warto sprawdzić
ręcznie przed publikacją, z sieci bez tych ograniczeń.

Żadne twierdzenie w tym dokumencie nie jest estymacją — gdzie nie znaleziono danych,
napisano to wprost jako "brak danych".

---

## Konkluzja na start (zgodnie z zasadą "jeśli 97% ma jednak źródło — powiedz to od razu")

**Statystyka "97%" NIE ma wiarygodnego źródła. Kąt artykułu się utrzymuje.**

Zbadano dwa warianty tego twierdzenia w kilkunastu niezależnych wystąpieniach, dwoma
niezależnymi ścieżkami researchu, i w żadnym przypadku nie znaleziono odniesienia do
realnego pomiaru, ankiety z metodologią, ani datasetu. Liczba jest niestabilna między
publikacjami (97%, 90%, 80% dla tego samego rytorycznego twierdzenia u różnych autorów)
— to sygnatura hooka marketingowego, nie faktu przenoszonego przez cytowanie.

---

## Sekcja 1 — Archeologia statystyki "97%"

### Dwa warianty twierdzenia (rozróżnione, bo to różne claimy)

- **Wariant A**: "97% workflow n8n nie ma error handlingu" — twierdzenie o stanie
  konfiguracji.
- **Wariant B**: "97% workflow, które działają w testach, failuje na produkcji" —
  twierdzenie o wyniku testowania/wdrożenia.

### Oś czasu

| Data | Źródło | Wariant | Cytat | Źródło podane? |
|---|---|---|---|---|
| ~8.06.2026¹ | YouTube, "Why 97% of n8n Workflows Fail in Production (And How to Fix It)" — https://www.youtube.com/watch?v=ASnwt2ilg28 | B | "An estimated 97% of n8n workflows that work perfectly during testing end up failing when they hit a live production environment." | Nie |
| ~18.06.2026¹ | Podcast AI Fire Daily #25 "Max" — https://rss.com/podcasts/ai-fire-daily/2079278/ (kopie: podm8.com, podcast24.fr) | B | wersja audio tej samej tezy ("4-Step Fix": Security, Retries & Fallbacks, Centralized Error Handling, Version Control) | Nie |
| ~22.06.2026¹ | Blog AI Fire (aifire.co) — https://www.aifire.co/p/why-your-n8n-automation-workflow-fails-how-to-fix-it | B | jak wyżej, rozwinięte | Nie, mimo wielokrotnych, celowanych zapytań o cytowanie źródła |
| brak ustalonej daty | Blog AI Fire — https://www.aifire.co/p/5-n8n-error-handling-techniques-for-a-resilient-automation-workflow | B/pokrewne | podobna narracja ("działa w testach, disaster strikes z realnymi danymi") | Nie |
| ~29.07.2026¹ | YouTube, inny twórca — https://www.youtube.com/watch?v=td5StBRZBJc | B | identyczna teza, **90%** zamiast 97% | Nie |
| 2026, bez daty | Medium — https://medium.com/@svnkrmkr/why-80-of-ai-workflow-automations-silently-fail-in-30-days-3a26d73f9c85 | B, poza n8n (ogólnie AI automation) | identyczna teza, **80%** | Nie |
| 30.01.2026 (data w URL) | Speedrun Ventures — https://speedrun.ventures/blog/2026-01-30-complete-guide-n8n-workflow-monitoring-error-handling/ | A | "The harsh reality: 97% of n8n workflows lack proper error handling." Autor podpisany jako "Jarvis, AI operations lead" | Nie |
| brak ustalonej daty, 2026 | PageLines — https://www.pagelines.com/blog/n8n-error-handling-patterns/ | A | "97% of n8n workflows lack proper error handling" | Nie |
| sporne | NextGrowth.ai — https://nextgrowth.ai/n8n-workflow-error-alerts-guide/ | A (niepotwierdzone) | jedna ścieżka researchu nie znalazła frazy 97% bezpośrednio na tej stronie w pełnym odczycie — możliwa konfuzja wyszukiwarki | Nie |

¹ Daty dla treści wideo/audio/blog pochodzą z metadanych zwróconych przez wyszukiwarkę
(rss.com, YouTube), nie z bezpośredniego odczytu strony — potwierdź ręcznie przed
publikacją, jeśli data ma znaczenie dla tezy "najwcześniejsze wystąpienie".

**Najwcześniejszy zidentyfikowany klaster**: pakiet treści AI Fire (aifire.co) —
wideo + podcast + blog, czerwiec 2026, wariant B. Nie znaleziono nic wcześniejszego mimo
wielokrotnych zapytań pod różne sformułowania obu wariantów. AI Fire to newsletter/marka
AI (aifire.co, ~330 tys. odbiorców wg crunchbase.com/organization/ai-fire-728e),
założona przez Adama Trana — profil content-marketingowy, nie badawczy.

### Łańcuch cytowań

Nie istnieje jawny łańcuch cytowań w sensie "artykuł X linkuje do źródła Y". Istnieje
za to **równoległe, nieopisane powielanie** tej samej rytorycznej figury retorycznej z
losowo dobieraną okrągłą liczbą:

```
Generacja 1 (czerwiec 2026) — wariant B, "fail w produkcji"
  AI Fire: wideo → podcast → blog (ta sama treść, ta sama marka, zero źródła)
        │
        ▼ (inny twórca podmienia liczbę pod ten sam hook — nie cytuje, tworzy od nowa)
  "90%" — inny kanał YouTube (~lipiec 2026)
  "80%" — inny autor, Medium, automatyzacja AI ogólnie (2026)

Generacja 2 (2026) — wariant A, mutacja na "brak error handlingu"
  Speedrun Ventures (30.01.2026) — zero źródła
  PageLines — zero źródła
```

Żadna z dziewięciu sprawdzonych publikacji nie podaje ankiety, datasetu, telemetrii
vendora ani pracy naukowej jako źródła.

### Czy to fabrykacja?

Ocena: **najprawdopodobniej tak**, na podstawie:

1. Zero cytowanych źródeł w dziewięciu niezależnie sprawdzonych wystąpieniach, w obu
   wariantach, na przestrzeni dwóch "generacji" treści (2026).
2. Liczba pływa między publikacjami (97/90/80%) dla identycznego claimu — sygnatura
   niezależnego doboru chwytliwej okrągłej liczby, nie propagacji faktu.
3. Warianty A i B to różne twierdzenia (jakość konfiguracji vs. wynik testowania), a
   mimo to dzielą tę samą liczbę między generacjami — bardziej zgodne z recyklingiem
   nagłówka niż z dwoma niezależnymi pomiarami trafiającymi przypadkiem w tę samą
   wartość.
4. Najwcześniejszy klaster to pakiet content-marketingowy (wideo+podcast+blog jednej
   marki w dwa tygodnie), nie publikacja badawcza.
5. Autorstwo części tekstów budzi wątpliwości co do pochodzenia (np. podpis "Jarvis, AI
   operations lead" na Speedrun Ventures — bez dającej się zweryfikować tożsamości).

### Sprawdzone fałszywe tropy (liczby "97%" niezwiązane z tezą, ale mogące być źródłem konfuzji)

- **n8n.io case studies**: klient "zredukował czas ręcznego wprowadzania danych o 97%"
  — https://n8n.io/case-studies/ — realna, ale zupełnie inna metryka (oszczędność
  czasu, nie awaryjność).
- **Ankieta WRITER 2026** ("97% firm wdrożyło agentów AI, tylko 11% w produkcji", ~2400
  respondentów) — realna, metodologicznie opisana ankieta, ale dotyczy wdrożeń agentów
  AI w ogóle, nie n8n i nie error handlingu:
  https://lumichats.com/blog/ai-agents-97-percent-deployed-11-percent-production-2026,
  https://www.themindfinders.com/2026/05/28/97-of-companies-have-deployed-ai-agents-79-are-still-struggling/
- **Ogólne statystyki porażek projektów IT/AI**: nie ma tam liczby 97% — realne cytowane
  wartości to m.in. 40% (Gartner, agentic AI projects cancelled do 2027 —
  https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027),
  68–85% (różne claimy o transformacji cyfrowej/AI), 80,3% (RAND, AI w przedsiębiorstwach).
  Żadna nie jest n8n-specyficzna i żadna nie wynosi 97% — więc transfer z innej dziedziny
  nie potwierdza się wprost, choć nie można wykluczyć nieudokumentowanego "zaokrąglenia
  w pamięci" przez autora AI Fire.

### Do zrobienia ręcznie przed publikacją

Jedna rzecz nie została zamknięta z powodu blokady sieciowej: bezpośrednie otwarcie
https://www.aifire.co/p/why-your-n8n-automation-workflow-fails-how-to-fix-it z innej
sieci i sprawdzenie, czy w pełnym HTML (nie w indeksowanym fragmencie wyszukiwarki) jest
jakikolwiek link/przypis przy zdaniu z "97%". To pojedyncza, wysoka wartość informacyjna
czynność, która domyka tę sekcję z pełną pewnością.

---

## Sekcja 2 — Inne niesourcowane statystyki w niszy automatyzacji

| # | Statystyka (verbatim) | Przykładowe URL-e cytujące | Deklarowane źródło | Weryfikacja | Ocena |
|---|---|---|---|---|---|
| 1 | "94% of workers say they perform repetitive, time-consuming tasks in their role" | docuclipper.com/blog/workflow-automation-statistics/, coworker.ai/blog/workflow-automation-statistics, quixy.com/blog/workflow-automation-statistics-and-forecasts/ | Niekonsekwentnie: część roundupów podaje "McKinsey Global Institute", część nic | Realne źródło to prawdopodobnie własna ankieta Zapiera "2021 State of Business Automation" (zapier.com/blog/state-of-business-automation-2021/), ~1000 pracowników USA, kwiecień 2021 — nie McKinsey | **Błędnie przypisane** + nieaktualne (ankieta vendora sprzed 5 lat cytowana jako ogólny fakt) |
| 2 | "McKinsey estimates that 60% of employees could save 30% of their time with workflow automation" | formstack.com/blog/workflow-automation-statistics, coworker.ai/blog/workflow-automation-statistics, cflowapps.com/workflow-automation-statistics/ | McKinsey | Realny raport McKinsey (2017, "A Future That Works"/MGI) mówi: "~60% zawodów ma co najmniej 30% czynności składowych możliwych do zautomatyzowania" — to stwierdzenie o technicznej automatyzowalności zadań, nie o realnej oszczędności czasu pracowników używających dziś narzędzi typu n8n/Zapier | **Zniekształcone** (realny raport, fałszywa parafraza) |
| 3 | "EY has seen as many as 30 to 50% of initial RPA projects fail" | metasource.com/document-management-workflow-blog/why-rpa-projects-fail/, blog.vsoftconsulting.com, futurecio.tech, cmswire.com | Raport EY "Get ready for robots" (~2016) | Konsekwentnie przypisywane do EY, ale nie znaleziono żywego, dostępnego dziś linku do oryginalnego raportu — same wtórne parafrazy | **Prawdopodobnie realne, ale niemożliwe do zweryfikowania u źródła** (martwy pierwotny dokument) |
| 4 | "internal data from 847 enterprise implementations shows that 73% of RPA initiatives fail to meet their business case projections within 24 months" | nigamr24.medium.com/the-automation-paradox-why-73-of-rpa-initiatives-fail-and-how-enterprise-leaders-are-breaking-27f7a20f2190 (25.08.2025) | "internal data" — bez nazwy firmy/badania | Żadnego drugiego, niezależnego cytowania nie znaleziono; podejrzanie precyzyjna liczba "847" bez żadnej proweniencji | **Fabrykacja** |
| 5 | "69% of RPA projects fail to take off because of their complexity" | cxotechmagazine.com/why-do-rpa-initiatives-fail-and-some-tips-to-avoid-failures/ | "a recent survey" (bez nazwy) | Brak nazwy ankiety, wydawcy, próby | **Niesourcowane** |
| 6 | Zapier: godziny oszczędzone tygodniowo wg roli (marketing 25h, IT 20h, obsługa klienta 16h, HR 8h, sprzedaż 6h, księgowość 4h) | zapier.com/blog/report-marketers-lead-automation-use/, growwstacks.com/blog/how-zapier-can-save-you-hours-every-week | Własna ankieta Zapiera (~1000 pracowników USA, lipiec 2021) | Metodologia istnieje i jest nazwana, ale to ankieta vendora wśród własnych klientów, przedstawiana w treściach 2025–2026 jako aktualny, neutralny fakt bez ujawnienia interesu vendora i wieku danych (4–5 lat) | **Sourced, ale stronnicze/nieaktualne** |
| 7 | Koszt przestoju "$5 600 za minutę" (Gartner) | dotcom-monitor.com/blog/what-is-the-cost-of-downtime/, systechmsp.com/what-it-downtime-really-costs/, moogsoft.com/downtime-calculator/ | Gartner | Realny szacunek Gartnera z 2014 r., wciąż cytowany w treściach 2025 jako aktualny, obok sprzecznych nowszych liczb ($9000, $12 900, $14 056, $23 750/min z innych źródeł) bez pojednania | **Błędnie przypisane przez wyrwanie z kontekstu/nieaktualność** |
| 8 | "25% of managers devote more than 20 hours weekly to repetitive administrative tasks" | thisandthat.chat/blog/workflow-efficiency-statistics/ (5.05.2026) | Brak podanego źródła | Brak jakiegokolwiek drugiego, niezależnego cytowania; blog vendora automatyzacji (this+that, Jeff Reynar) bez linkowanego badania | **Niesourcowane** |
| 9 | "51% of employees spend at least two hours daily on repetitive tasks" | thisandthat.chat/blog/workflow-efficiency-statistics/ (ten sam artykuł co #8) | Brak podanego źródła | Jak wyżej | **Niesourcowane** |
| 10 | Boilerplate case-study n8n: "cięcie czasu operacyjnego do 92%, 15+ godzin oszczędności tygodniowo, wzrost konwersji do 40%" | duotach.com/en/blog/casos-exito-automatizacion-n8n-argentina i niemal identyczne sformułowania na techbuddies.io, aiadoptionagency.com, robizsolutions.com, automatespot.com | Nienazwany klient ("sieć aptek", "klient AdTech") | Ta sama treść powtórzona niemal słowo w słowo na wielu blogach niskiej wiarygodności SEO, żaden nie linkuje do pierwotnego case study z nazwanym klientem. Oficjalna strona n8n.io/case-studies/ nazywa realne firmy (np. Delivery Hero, StepStone) z innymi, skromniejszymi liczbami — kombinacja 92%/40% wygląda na treść typu "blogspam", nie materiał od n8n | **Fabrykacja/niesourcowane** |

**Podsumowanie**: 2 fabrykacje (#4, #10), 3 błędnie przypisane (#1, #2, #7), 3
niesourcowane (#5, #8, #9), 2 sourced-ale-niezweryfikowalne/przeterminowane (#3, #6, jako
kontrastowy przypadek "wygląda na realne, ale nie da się dziś sprawdzić u źródła").

---

## Sekcja 3 — Datasety gotowe do re-analizy (najważniejsza sekcja)

### 3.1 github.com/Zie619/n8n-workflows — sprawdzone bezpośrednio (git clone + GitHub API, wysoka pewność)

- **Licencja**: MIT (plik `LICENSE`, potwierdzone treścią pliku i polem `license.spdx_id: "mit"` z GitHub API). Pozwala na użycie, kopiowanie, modyfikację, publikację bez ograniczeń; jedyny wymóg to zachowanie noty copyright przy kopiach *oprogramowania* — publikacja zagregowanych metryk nie jest tym objęta wprost, ale tania atrybucja jest bezpieczna.
- **KLUCZOWA ROZBIEŻNOŚĆ**: README oraz wygenerowany plik `docs/api/stats.json`
  (znacznik czasu `2025-11-03T21:12:58`) deklarują **4 343 workflow**, 29 445 nodów, 365
  integracji. Bezpośrednie policzenie plików w najnowszym commicie
  (`find workflows -name "*.json" | wc -l`) daje **2 061 plików JSON** — ok. **47% tego,
  co deklaruje README/badge**. Potwierdzone dwukrotnie: raz przez sklonowanie repo
  agentem badawczym, raz przez bezpośredni WebFetch tej samej strony GitHub (README nadal
  pokazuje 4343 na dziś, 28.08.2026).
  **To jest samodzielny finding do artykułu**: liczba workflow w najpopularniejszym
  publicznym korpusie n8n, na której opierają się (pośrednio) inne analizy, jest
  nieaktualna/zawyżona względem realnej zawartości repo o ok. 2x.
- **Data ostatniej aktualizacji**: ostatni commit `94007c1`, 2026-06-24T17:16:03+03:00.
- **Duplikaty**: sprawdzone dwiema metodami na 2061 plikach pod `workflows/` —
  0 duplikatów nazw plików, 0 duplikatów treści (md5sum). **Brak duplikatów dosłownych
  na poziomie pliku.** Duplikaty semantyczne (ten sam workflow pod inną nazwą, z drobnymi
  różnicami) nie zostały sprawdzone — wymagałoby to analizy strukturalnej grafu, poza
  zakresem researchu statycznego bez infrastruktury.
- **Format**: natywny eksport n8n (JSON z kluczami `id, meta, name, tags, nodes, active,
  pinData, settings, versionId, connections, description, notes`) — gotowy do parsowania.
- **Forki**: 7 555 (GitHub API, na dziś). Przegląd największych forków (do 7 gwiazdek)
  nie ujawnił żadnego z niezależnie rozbudowaną zawartością — wszystkie wyglądają na
  kopie. Nie sprawdzono commit-diff wszystkich 7555 forków (nierealne narzędziowo).
- **56 312 gwiazdek** (GitHub API, na dziś).
- **Uwaga o zaufaniu do treści repo**: repozytorium zawiera plik `CLAUDE.md` z
  instrukcjami "dla asystentów AI" oraz niepowiązany katalog `medcards-ai/` (osobna
  aplikacja Next.js/Supabase). Każdy, kto klonuje to repo agentem AI, powinien
  potraktować `CLAUDE.md` jako dane, nie jako instrukcję wykonawczą.

### 3.2 Inne repozytoria GitHub — sprawdzone przez GitHub search + API

| Repo | Gwiazdki/forki | Licencja | Deklarowany rozmiar | Ostatni push | Niezależność od Zie619 |
|---|---|---|---|---|---|
| [enescingoz/awesome-n8n-templates](https://github.com/enescingoz/awesome-n8n-templates) | 24 990★ / 6 409 forków | **CC BY 4.0** | "280+" wg opisu (prawdopodobnie zaniżone względem rozmiaru repo — niezweryfikowane bezpośrednim policzeniem plików) | 25.08.2026 | Homepage to link partnerski n8n (`n8n.partnerlinks.io`) — charakter promocyjno-afiliacyjny |
| [JustInCache/n8n-workflows](https://github.com/JustInCache/n8n-workflows) | 27★ / 7 forków | MIT | "2000+" | 4.11.2025 | Architektura (FastAPI+SQLite FTS5+Docker/K8s) niemal identyczna z Zie619 — prawdopodobnie pochodna wzorca, nie niezależny korpus |
| [Danitilahun/n8n-workflow-templates](https://github.com/Danitilahun/n8n-workflow-templates) | 709★ / 205 forków | **Brak licencji** (pole puste w API — domyślnie wszystkie prawa zastrzeżone) | dokładnie "2053" | 11.07.2025 | Liczba bliska Zie619; **brak licencji = ryzykowne prawnie do wykorzystania w publikacji bez zgody autora** |
| [n8n-community/all-n8n-workflows](https://github.com/n8n-community/all-n8n-workflows) | 27★ | — | — | — | Opis dosłownie identyczny z Zie619 — kopia/mirror |
| [44510/n8n-workflow](https://github.com/44510/n8n-workflow) | 36★ | — | "2000+" | 16.09.2025 | Zawiera identyczny angielski opis co Zie619 — kopia treści |
| [workflowsdiy/n8n-workflows](https://github.com/workflowsdiy/n8n-workflows) | 47★ / 29 forków | — | repo 359 KB — mały zbiór | 27.05.2025 | Za mały, by być niezależnym dużym korpusem |
| [simealdana/ai-automation-jsons](https://github.com/simealdana/ai-automation-jsons) | 39★ / 16 forków | — | repo 19 KB | 21.05.2025 | Marginalny rozmiarowo |

**Wniosek**: poza enescingoz (CC BY 4.0, duży, ale afiliacyjny), praktycznie wszystkie
duże "kolekcje workflow n8n" na GitHubie są kopiami/pochodnymi tego samego wzorca
zapoczątkowanego przez Zie619 — nie niezależnymi korpusami zebranymi inną metodą. Nie
znaleziono żadnego dużego (rzędu tysięcy) zbioru z jednoznacznie innym źródłem danych i
jasną permisywną licencją poza tymi dwoma.

Dodatkowo (poza zakresem GitHuba, niezweryfikowane — huggingface.co zablokowane w tej
sesji): zbiory na Hugging Face (`mbakgun/n8nbuilder-n8n-workflows-dataset`,
`npv2k1/n8n-workflow`, `ruh-ai/n8n-workflow-dataset`, `eclaude/n8n-workflows-sft`) —
trop do dalszego sprawdzenia, nie zweryfikowane ustalenie.

### 3.3 Oficjalna biblioteka template'ów n8n.io

- **Liczba template'ów**: ~**11 741** na sierpień 2026 (potwierdzone niezależnie dwoma
  zapytaniami wyszukiwarki, zbieżne z ~11 774 z pierwszego przebiegu; kategoria AI ~8 002
  z 11 741, czyli ~69%). Średniej pewności — oparte na fragmentach wyszukiwarki, nie na
  bezpośrednim odczycie strony (n8n.io zablokowane w tej sesji).
- **API**: wyniki wyszukiwania wskazują na istnienie endpointów
  `api.n8n.io/templates/search`, `/templates/categories`, `/templates/collections`,
  `/templates/workflows/{id}`, `/schema` — **niepotwierdzone bezpośrednim zapytaniem**
  (domena zablokowana w tej sesji). Do zweryfikowania ręcznie przed budową jakiegokolwiek
  narzędzia opierającego się na tym API.
- **ToS dot. automatycznego pobierania**: **brak danych w wymaganym stopniu pewności**
  (dokładny cytat + bezpośrednio zweryfikowany URL). Znaleziono tylko pośrednią poszlakę
  — fragment przypisywany do `n8n.io/legal/self-serve-terms/`: *"You will not reverse
  engineer or otherwise attempt to derive or obtain information about the functioning,
  manufacture or operation of the Cloud Services."* — to dotyczy usługi Cloud (SaaS), nie
  jednoznacznie publicznej galerii template'ów, i nie zostało zweryfikowane bezpośrednim
  odczytem dokumentu. **Przed jakimkolwiek działaniem opierającym się na API n8n.io
  koniecznie przeczytać `n8n.io/legal/self-serve-terms/` i
  `n8n.io/legal/customer-acceptable-use-policy/` w całości z sieci bez blokad.**

### 3.4 Praca "Characterizing Large Language Model Agentic Workflows: A Study on N8n Ecosystem" (arXiv:2606.29116) — ODPOWIEDŹ WPROST

**Nie znaleziono potwierdzonego, zweryfikowalnego linku do opublikowanego datasetu,
replication package ani kodu tej pracy.**

- **Identyfikacja**: arXiv:2606.29116, autorzy **Yutian Tang, Yuming Zhou, Huaming Chen**
  (potwierdzone przez wyszukiwarkę — https://arxiv.org/abs/2606.29116, v2:
  https://arxiv.org/abs/2606.29116v2, zgłoszenie ~27.06.2026, rewizja v2 ~11.07.2026).
- **Korpus**: 6 003 poprawne pliki JSON workflow n8n, filtrowane pod obecność komponentu
  LLM (node providera LLM, node agenta AI, node modelu czatu, lub wywołania HTTP/API
  pasujące do znanych endpointów LLM — OpenAI, Anthropic, Hugging Face, Gemini, Mistral,
  Ollama, LangChain itd.). Źródło opisane w streszczeniach jako "publicznie dostępne
  szablony/ekosystem n8n" — sformułowanie sugerujące raczej katalog n8n.io/workflows niż
  Zie619 (żadna z liczb Zie619 — ani historyczne 4343, ani realne 2061 — nie pasuje do
  6003), ale to wnioskowanie, nie potwierdzony fakt.
- **Data availability**: arxiv.org było zablokowane w tej sesji na poziomie sieciowym dla
  bezpośredniego odczytu (PDF/HTML), więc sekcja "Data Availability"/"Threats to
  Validity" nie została przeczytana wprost. W jednym przebiegu wyszukiwarki pojawiło się
  zdanie sugerujące, że "autorzy opublikowali dataset, framework analizy i replication
  package" — **ale bez towarzyszącego URL-a**, i powtórzenie zapytania nie odtworzyło
  tego twierdzenia ani nie dało linku. Oceniamy to zdanie jako niewiarygodne/możliwe
  halucynowane podsumowanie wyszukiwarki i **nie liczymy go jako potwierdzenia
  publikacji danych.**
- **Konsekwencja dla artykułu**: jeśli praca faktycznie nie publikuje danych, to żadna z
  metryk niezależności podanych przez autorów (patrz Sekcja 4 — error handling, reliability
  mechanisms) nie da się rozszerzyć ani zweryfikować bez odtworzenia ich metodologii
  doboru workflow od zera, bez pewności trafienia w te same 6003 pliki.
- **Rekomendacja — jedyna czynność w całym raporcie wymagająca ręcznego sprawdzenia z
  sieci bez blokad**: otworzyć https://arxiv.org/abs/2606.29116v2 (oraz PDF), sprawdzić
  przypisy, sekcję Data/Code Availability i Limitations/Threats to Validity. To
  rozstrzyga ostatecznie pytanie z brief-u.

### 3.5 Inne prace naukowe o n8n/Make/Zapier z otwartymi danymi

**Brak danych.** Nie znaleziono żadnej innej pracy empirycznie analizującej n8n, Make.com
lub Zapier z opublikowanym, otwartym datasetem workflow, poza pracą z 3.4. Sprawdzone i
odrzucone jako nietrafne: "An Empirical Study of the Evolution of GitHub Actions
Workflows" (arxiv.org/pdf/2602.14572 — dotyczy CI/CD, nie n8n), "An Empirical Study of
Developer Discussions on Low-Code Software Development Challenges"
(arxiv.org/pdf/2103.11429) i "An Empirical Study on Low-Code Programming"
(arxiv.org/pdf/2402.01156) — dotyczą low-code ogólnie (ankiety deweloperów), nie analizy
korpusu workflow.

### 3.6 Oficjalne statystyki użycia n8n (firma)

- **github.com/n8n-io** (sprawdzone bezpośrednio): ~47 repozytoriów, głównie silnik
  `n8n`, `n8n-docs`, `n8n-hosting`, `n8n-nodes-starter`,
  `self-hosted-ai-starter-kit`, infrastruktura. **Brak repo z datasetem workflow,
  statystykami użycia czy raportem "state of automation".**
- **Oficjalny raport roczny/"State of Automation"**: **brak danych** — nie znaleziono na
  blog.n8n.io ani community.n8n.io mimo kilku wariantów zapytań.
- Liczby krążące w serwisach trzecich (raascloud.io, ahrefs.com/websites/n8n.io — np.
  wycena $2,5 mld, 150–230 tys.+ aktywnych użytkowników, 10,73 mln odwiedzin/mies.
  styczeń 2026) to **agregaty SEO-blogów, nie oficjalne dane n8n** — nie cytować jako
  faktu bez dalszej weryfikacji.

### Podsumowanie sekcji 3 — co jest realnie użyteczne do statycznej re-analizy

1. **Zie619/n8n-workflows** (MIT) — najlepiej udokumentowany, realnie **2061** (nie 4343)
   unikalnych surowych eksportów JSON, 0 duplikatów dosłownych, aktualny na 24.06.2026.
   Najbezpieczniejszy prawnie i najbardziej przejrzysty wybór.
2. **enescingoz/awesome-n8n-templates** (CC BY 4.0) — duży, permisywnie licencjonowany,
   deklarowana liczba do zweryfikowania bezpośrednim policzeniem plików przed użyciem.
3. **arXiv 2606.29116** — najbogatszy metodologicznie (6003 workflow z filtrem LLM), ale
   **bez potwierdzonego publicznego datasetu** — wymaga ręcznej weryfikacji z sieci bez
   blokad, patrz 3.4.
4. Pozostałe repozytoria GitHub to w większości kopie/pochodne tego samego wzorca.

---

## Sekcja 4 — Co już zostało policzone, a co nie

**Uwaga**: żadna z poniższych liczb (poza duplikatami w Zie619, patrz 3.1) nie pochodzi
z jawnie zdeduplikowanego korpusu — patrz ostatni wiersz tabeli.

| Metryka | Zmierzone? | Źródło + URL + data | Liczba/% | Uwagi o metodologii |
|---|---|---|---|---|
| 1. Odsetek workflow z Error Workflow na poziomie ustawień | Częściowo, proxy niedokładny | arXiv 2606.29116 (2026) — https://arxiv.org/abs/2606.29116 | 1829/6003 (~30,5%) ma "platform-level error handling"; 684/6003 (~11,4%) ma anchor do outputu LLM | Korpus = tylko workflow z komponentem LLM/agentowym, nie ogólna populacja n8n. Definicja "platform-level error handling" niepotwierdzona w pełnym tekście (arxiv.org zablokowane). **Nota dla artykułu**: to jest najbliższa istniejąca liczba kontrująca claim "97% nie ma error handlingu" — nawet w wąskiej, wyselekcjonowanej próbie LLM-workflow ok. 30% JEDNAK ma jakąś formę error handlingu, więc nawet gdyby "97%" miało dotyczyć tego zjawiska, nie zgadza się z jedynym istniejącym pomiarem |
| 2. Odsetek nodów z retryOnFail + jakość backoff | Nie | — | — | Brak danych. Istnieją wyłącznie poradniki normatywne ("jak to zrobić", np. easify-ai.com, n8nlogic.com) — zero pomiaru rzeczywistej prewalencji |
| 3. Odsetek workflow z webhookiem bez uwierzytelnienia | **Tak** | Blog Aironclaw, "We audited 12K n8n templates: most have critical vulnerabilities" — https://blog.aironclaw.com/n8n-12k-templates-critical-vulnerabilities/, 19.05.2026 (potwierdzenie na X: https://x.com/rev3rsesecurity/status/2056822023016341892) | 2171/12750 (~17,0%) bez auth; 2488/12750 (19,5%) uznane za "real-exploitable pre-auth"; 38 workflow z potencjalnym RCE (node shell/ssh) | Korpus = top 1000 z n8n.io + 8 największych repo GitHub, **bez udokumentowanej deduplikacji** — wysokie ryzyko zawyżonego mianownika, biorąc pod uwagę ustalenie z Sekcji 3, że większość dużych repo GitHub to kopie tego samego korpusu. Skaner własny firmy audytującej — metodologia detekcji nie w pełni opisana w dostępnych fragmentach |
| 4. Wzorce idempotencji (dedup checks, idempotency keys) | Nie | — | — | Brak danych. Obfita literatura poradnikowa (Medium, abhiman.io, kriv.ai, 8kit.io) opisująca *jak* to zrobić — zero pomiaru *ile osób to robi* |
| 5. Jawny throttling / rate limiting | Nie | — | — | Brak danych. Poradniki (medium.com/@Modexa, growwstacks.com) bez pomiaru prewalencji |
| 6. Walidacja danych wejściowych | Nie | — | — | Brak danych. Istnieje community node "Data Validation" (JSON Schema), dokumentacja jak używać IF/Switch — zero pomiaru odsetka workflow faktycznie to robiących |
| 7. **Deduplikacja korpusu (unikalne vs kopie/warianty)** | **Nie — nikt tego formalnie nie sprawdził** | — | — | Najważniejsze pojedyncze ustalenie tej sekcji: żadna ze znalezionych publikacji ilościowych (Aironclaw, arXiv 2606.29116) nie opisuje procedury deduplikacji źródła. Pośredni dowód na istnienie problemu: zgłoszony bug w n8n Creator Hub, gdzie błąd przy submisji powoduje wielokrotne duplikaty tego samego workflow w galerii bez możliwości usunięcia — https://community.n8n.io/t/creator-hub-fetcherror-400-on-workflow-submission-duplicate-workflows-impossible-to-delete/282910 (dowód anegdotyczny, nie pomiar skali). Zie619 (Sekcja 3.1) jest jedynym sprawdzonym korpusem z potwierdzonym brakiem duplikatów dosłownych (0/2061), ale nie sprawdzono duplikatów semantycznych nawet tam |

**Wniosek dla artykułu**: dwie jedyne twarde, cytowalne liczby w temacie niezawodności
n8n to (a) ~17,0% webhooków bez auth / ~19,5% "real-exploitable pre-auth" z audytu
Aironclaw (12 750 szablonów, maj 2026), oraz (b) ~30,5% workflow LLM-owych z
"platform-level error handling" z arXiv 2606.29116 (6003 workflow). Obie powinny być
prezentowane z zastrzeżeniem, że żadna nie pochodzi z jawnie zdeduplikowanego korpusu —
a sama deduplikacja (metryka 7) jest całkowicie niezmierzona przez kogokolwiek, co samo
w sobie jest istotną luką badawczą wartą wyeksponowania w artykule. Metryki 2, 4, 5, 6 są
całkowicie niezmierzone — istnieje wyłącznie literatura normatywna.

---

## Sekcja 5 — Ryzyka publikacyjne

*Zastrzeżenie: to nie jest porada prawna. Przed publikacją zalecana konsultacja z
prawnikiem znającym prawo polskie oraz podstawy prawa UE i common law (publikacja będzie
czytana globalnie). n8n GmbH jest zarejestrowana w Niemczech.*

### 5.1 Co wolno opublikować z repo MIT zawierającego workflow pierwotnie z n8n.io

**Licencja MIT** (tekst z pliku LICENSE Zie619/n8n-workflows,
https://github.com/Zie619/n8n-workflows/blob/main/LICENSE): zezwala na użycie, kopiowanie,
modyfikację, publikację, dystrybucję, sublicencjonowanie, sprzedaż — bez ograniczeń;
wymaga zachowania noty copyright i tekstu licencji przy kopiach lub "istotnych
fragmentach" Software. Nie ma gwarancji ani odpowiedzialności autorów.

**Kwestia interpretacyjna**: licencja MIT repozytorium dotyczy kodu/infrastruktury tego
repo (skrypty, README). Nie jest jasne, czy autor repo miał prawo objąć licencją MIT same
treści workflow pochodzące od osób trzecich publikujących w bibliotece n8n.io — README
nie zawiera oświadczeń o prawach do poszczególnych plików ani o zgodności z ToS n8n.io.

**Terms of Service n8n.io** (https://n8n.io/legal/self-serve-terms/, treść zweryfikowana
pośrednio przez wyszukiwarkę, zalecana bezpośrednia lektura przed publikacją): twórca
Community Content (workflow w bibliotece) zachowuje prawa autorskie, n8n dostaje jedynie
licencję do wyświetlania. To oznacza, że repozytorium GitHub, które zebrało workflow z
n8n.io i objęło je własną licencją MIT, potencjalnie nie miało do tego pełnego prawa
wobec workflow, których nie jest autorem. **To ryzyko leży po stronie repozytorium
źródłowego (Zie619 itp.), nie po stronie badacza analizującego dalej ten dataset** — co
jest argumentem za publikowaniem zagregowanych metryk, nie surowych treści.

**Fakty vs. utwory — Feist v. Rural Telephone (US, 1991,
https://supreme.justia.com/cases/federal/us/499/340/)**: fakty nie podlegają ochronie
prawnoautorskiej, chroniona jest tylko oryginalna "selection, coordination, and
arrangement". Statystyka typu "X% z N workflow ma cechę Y" to fakt/wynik analizy, nie
utwór — publikacja takiej metryki nie narusza praw autorskich do poszczególnych
workflow. To zasada USA; analogiczna dychotomia idea/ekspresja obowiązuje w UE.

**Prawo sui generis do baz danych (dyrektywa UE 96/9/EC,
https://www.wipo.int/wipolex/en/text/126788)**: chroni "istotną inwestycję" w bazę danych
przed ekstrakcją/reużyciem "istotnej części" jej zawartości. To ryzyko odrębne od
copyrightu, potencjalnie dotyczące n8n.io jako twórcy bazy (biblioteka 11 741 template'ów,
zorganizowana, przeszukiwalna) — nie samego repozytorium GitHub. Zagregowana statystyka
nie stanowi "reużycia istotnej części" w sensie ilościowym ani jakościowym — silny
argument za bezpieczeństwem publikowania metryk.

**Rekomendacja per kategoria treści**:

| Kategoria | Rekomendacja | Uzasadnienie |
|---|---|---|
| ID workflow | Bezpieczne | Identyfikator, nie utwór |
| URL-e źródłowe do oryginalnych template'ów | Bezpieczne, zalecane | Standard transparentności/replikowalności w badaniach i dziennikarstwie |
| Hashe (dedup) | Bezpieczne | Nieodwracalna transformacja, nie zawiera treści |
| Zagregowane metryki ("X% z N") | Bezpieczne — najniższe ryzyko | Fakty nie są chronione (Feist); nie stanowią "istotnej części" bazy danych |
| Fragmenty JSON / screenshoty konkretnej konfiguracji | Ryzyko umiarkowane — używać oszczędnie, anonimizować właściciela, cytować minimalny wycinek w celu ilustracyjnym | To już "istotny fragment" w rozumieniu MIT i potencjalnie prawa do bazy danych n8n.io |

### 5.2 Jak inni wskazują konkretne "złe" przykłady

- **GitGuardian "State of Secrets Sprawl"** (https://blog.gitguardian.com/the-state-of-secrets-sprawl-2026/,
  https://www.gitguardian.com/state-of-secrets-sprawl-report-2025): publikuje zagregowane
  statystyki (29 mln nowych sekretów w 2025, wzrost 34% r/r), **nie nazywa konkretnych
  repozytoriów ani właścicieli** — wzorzec adekwatny do błędów niedoświadczenia
  (workflow bez error handlingu to błąd, nie zła wola).
- **Sonatype/Socket.dev** (https://socket.dev/blog/surveillance-malware-hidden-in-npm-and-pypi-packages):
  nazywa wprost pakiety npm/PyPI zawierające malware — bo to artefakt stworzony w złej
  wierze, nie przypadkowy błąd. Ten wzorzec **nie pasuje** do sytuacji artykułu.
- **Responsible disclosure (Shodan/badacze bezpieczeństwa)**: najpierw prywatne
  powiadomienie właściciela, publikacja z nazwą *po* naprawie lub braku odpowiedzi w
  rozsądnym czasie (https://blog.shodan.io/security-researchers-find-vulnerable-iot-devices-and-mongodb-databases-exposing-corporate-data/).
- **Rekomendacja dla artykułu**: nazywać repozytorium-dataset źródłowy (to publiczny,
  świadomy projekt kuratorski), ale **nie identyfikować pojedynczych autorów-amatorów**
  konkretnych template'ów w bibliotece n8n.io, chyba że przykład jest oficjalnym,
  promowanym template'em n8n (wtedy krytyka celuje w n8n jako kuratora, silniej
  uzasadniona interesem publicznym). Ewentualne znalezione hardkodowane sekrety/klucze —
  nigdy nie publikować ich treści, zgłosić prywatnie, publikować tylko fakt zbiorczy.

### 5.3 Ryzyko krytyki niesourcowanej statystyki z podaniem nazwy konkretnych blogów

- **Doktryna "fair comment"** (common law): chroni opinię opartą na prawdziwych,
  weryfikowalnych faktach w sprawie interesu publicznego
  (https://www.mlflitigation.com/media/the-defence-of-fair-comment-in-defamation-claims/).
  Zdanie *"blog X twierdzi, że 97%, nie podając źródła"* jest **weryfikowalnym
  stwierdzeniem faktu** (sprawdzalne: czy blog X tak napisał i czy nie podał źródła), nie
  oceną — nawet nie potrzebuje tej obrony, o ile jest prawdziwe i precyzyjne. Ryzykowne
  byłoby dodanie interpretacji motywu ("kłamią celowo").
- **Polska (art. 212 KK, exceptio veritatis)**: prawda jest pełną obroną przed
  zniesławieniem; granica przebiega między *faktem* a *oceną*. "Ta statystyka nie ma
  źródła" to fakt sprawdzalny.
- **Defamation Act 2013 (UK)** jako punkt odniesienia dla "libel tourism": wprowadza próg
  "serious harm"/"serious financial loss" dla podmiotów gospodarczych oraz s.9
  ograniczające jurysdykcję dla powodów spoza UK/EU/EFTA
  (https://hamlins.com/insight/a-decade-of-the-defamation-act-2013-part-4-single-publication-and-jurisdiction/)
  — sama krytyka faktograficzna raczej nie osiąga tego progu.
- **IFCN/Poynter Code of Principles**
  (https://ifcncodeofprinciples.poynter.org/about): sygnatariusze fact-checkingowi
  podają źródła w stopniu pozwalającym czytelnikom samodzielnie zweryfikować ustalenia —
  nazwanie źródła wprost jest zgodne z najlepszymi praktykami branży, pod warunkiem
  dokładnego cytatu, linku, daty dostępu i gotowości na sprostowanie.

### Rekomendacje końcowe (Sekcja 5)

**Bezpieczne**: zagregowane metryki własnej analizy; nazwa i URL repozytorium-datasetu z
jego licencją; ID/hashe/URL-e do oryginałów; nazwanie konkretnych blogów w krytyce
niesourcowanej statystyki, sformułowane jako fakt weryfikowalny, z dokładnym cytatem i
linkiem.

**Unikać/ostrożnie**: publikacja pełnych JSON-ów lub sekretów/tokenów znalezionych w
danych (zgłosić prywatnie); szerokie fragmenty/screenshoty z identyfikacją
pojedynczego twórcy-amatora; zarzuty motywacyjne ("kłamią", "manipulują celowo") zamiast
faktograficznych ("nie znaleźliśmy podanego źródła").

---

## Sekcja 6 — Dystrybucja pod kątem debunkingowym

Kanały, które w ostatnich 24 miesiącach (sierpień 2024 – sierpień 2026) podchwytywały
materiał typu "popularna statystyka nie ma źródła, ktoś to policzył naprawdę" w
kontekście tech/software/data:

1. **Hacker News** — https://news.ycombinator.com — najsilniejszy dystrybutor tego typu
   treści. Przykład: wątek o "95% of generative AI pilots... failing" (raport MIT NANDA)
   — https://news.ycombinator.com/item?id=44941118 — dyskusja podważająca metodologię (52
   wywiady, brak peer review). Też trzy wątki o "ghost engineers" (rzekome 9,5–14%
   inżynierów "nic nie robiących", Stanford) —
   https://news.ycombinator.com/item?id=42361056,
   https://news.ycombinator.com/item?id=42284502,
   https://news.ycombinator.com/item?id=42257693.
2. **Sean Goedecke (blog)** — https://www.seangoedecke.com/why-do-ai-enterprise-projects-fail/
   (3.11.2025) — rozbija ten sam raport MIT NANDA, pokazując, że realny wskaźnik sukcesu
   wśród firm, które faktycznie próbowały wdrożenia, to ~8,3%, nie "95% porażek" z
   nagłówka.
3. **The Pragmatic Engineer — Gergely Orosz** —
   https://newsletter.pragmaticengineer.com/p/are-reports-of-stackoverflows-fall —
   konfrontuje viralowy "spadek ruchu SO o 50%" z wyjaśnieniem samego Stack Overflow
   (błąd w danych GA, realny spadek ~5%).
4. **Eric Holscher** — https://www.ericholscher.com/blog/2025/jan/21/stack-overflows-decline/
   (21.01.2025) — analiza oparta na oryginalnym datasecie, udostępnionym do samodzielnej
   weryfikacji przez czytelników.
5. **AI Snake Oil — Arvind Narayanan, Sayash Kapoor** — https://www.aisnakeoil.com/ —
   newsletter Princeton, cały profil to systematyczny debunking hype'u AI. Brak
   potwierdzonego pojedynczego URL-a z tej sesji (WebFetch zablokowane) — dodany na
   podstawie silnie potwierdzonego profilu tematycznego.
6. **Pivot to AI — David Gerard** —
   https://pivot-to-ai.com/2026/01/29/the-job-losses-are-real-but-the-ai-excuse-is-fake/
   (29.01.2026) — kwestionuje przypisywanie zwolnień w tech do AI.
7. **Statistical Modeling, Causal Inference and Social Science — Andrew Gelman** —
   https://statmodeling.stat.columbia.edu/2026/01/18/retroactively-validated-hype/
   (18.01.2026) — tytuł potwierdzony, treść niezweryfikowana w pełni (WebFetch
   zablokowane).
8. **Lost Boy — Leigh Dodds** — https://blog.ldodds.com/ — profil idealnie pasujący
   ("czy data scientist naprawdę spędza 80% czasu na czyszczeniu danych?"), ale
   znaleziony konkretny przykład
   (https://blog.ldodds.com/2020/01/31/do-data-scientists-spend-80-of-their-time-cleaning-data-turns-out-no/)
   jest z 2020 r. — poza oknem 24 miesięcy. Brak nowszego odpowiednika znalezionego w tej
   sesji.
9. **diginomica** — https://diginomica.com/data-science-myths-and-realities-do-data-scientists-really-spend-80-their-time-wrangling-data
   — data niepotwierdzona (WebFetch zablokowane), treściowo pasuje.
10. **Medium — Chris Dunlop** —
    https://medium.com/realworld-ai-use-cases/mit-report-claims-95-of-ai-projects-fail-this-report-is-utter-nonsense-a3c5b9f9a50b
    — prowokacyjny tytuł jako podręcznikowy przykład debunkingowego framingu.
11. **n8n Community Forum** — https://community.n8n.io/t/the-harsh-truth-of-selling-automations/192259
    (22.09.2025) — demontuje mit "umiesz budować w n8n = automatycznie zarabiasz". Jedyny
    potwierdzony przykład bezpośrednio z niszy n8n, choć dotyczy mitu biznesowego, nie
    statystyki liczbowej sensu stricto.
12. **Better Offline / Where's Your Ed At — Ed Zitron** —
    https://edzitron.spicytakes.org/post/2026-08-04-the-ai-demand-bubble (4.08.2026) —
    kwestionuje koncentrację przychodów AI; wywołał też kontr-debunking
    (https://www.obsolete.pub/p/ed-zitron-just-disproved-the-core) — dobry przykład
    żywej dyskusji o źródłach liczb w tej niszy.
13. **r/programming** — https://www.reddit.com/r/programming/ — dodany na podstawie
    profilu tematycznego, brak potwierdzonego konkretnego przykładu z ostatnich 24
    miesięcy (reddit.com zablokowane w tej sesji).
14. **Lobste.rs** — https://lobste.rs/ — jak wyżej, profil pasujący, brak potwierdzonego
    konkretnego przykładu.
15. **r/n8n, r/automation, r/nocode** — https://www.reddit.com/r/n8n/,
    https://www.reddit.com/r/automation/, https://www.reddit.com/r/nocode/ —
    bezpośrednio w niszy zamówionej przez brief, ale **niepotwierdzone w tej sesji**
    (reddit.com zablokowane) — zweryfikować bezpośrednio przed użyciem w planie
    dystrybucji.

**Kluczowa obserwacja**: najsilniejszy działający wzorzec w tej niszy to "popularna
statystyka X% → ktoś przeliczył surowe dane z oryginalnego źródła → okazuje się Y%" —
dokładnie kąt tego artykułu. Co konkretnie działa: prowokacyjny tytuł kontrujący viralową
liczbę, dostęp do oryginalnego datasetu do samodzielnej weryfikacji przez czytelnika,
wskazanie konkretnej wady metodologii (mała próba, brak peer review, konflikt interesu).
Nisza n8n/no-code **nie ma jeszcze** ugruntowanej kultury "citation archaeology" — to
realna luka do zagospodarowania.

---

## Otwarte pytania do ręcznej weryfikacji (z sieci bez blokad egress)

1. Pełny odczyt https://www.aifire.co/p/why-your-n8n-automation-workflow-fails-how-to-fix-it
   — czy w pełnym HTML jest jakikolwiek link/przypis przy zdaniu z "97%" (Sekcja 1).
2. Pełny odczyt https://arxiv.org/abs/2606.29116v2 (PDF/HTML) — sekcja Data/Code
   Availability, Limitations — rozstrzyga ostatecznie pytanie o replication package
   (Sekcja 3.4).
3. Pełny tekst https://n8n.io/legal/self-serve-terms/ i
   https://n8n.io/legal/customer-acceptable-use-policy/ — dokładne brzmienie klauzul o
   automatycznym pobieraniu danych z biblioteki template'ów (Sekcja 3.3, 5.1).
4. Bezpośrednie policzenie plików w enescingoz/awesome-n8n-templates (deklarowane "280+"
   wygląda na zaniżone względem skali repo — 25 tys. gwiazdek) (Sekcja 3.2).
5. Weryfikacja istnienia i rozmiaru r/n8n, r/automation, r/nocode oraz świeższy niż 2020
   przykład na blog.ldodds.com/diginomica (Sekcja 6).
