# Jak pracujemy w repozytorium

Krótka instrukcja dla całego zespołu: jak wziąć zadanie, założyć branch, zrobić pull request i korzystać z tablicy.

## Zasady w skrócie

- **Nikt nie pushuje bezpośrednio na `main`.** Wszystko idzie przez branch i pull request (PR).
- **Jedno zadanie = jedno issue = jeden branch = jeden PR.**
- Każdy PR musi mieć przegląd innej osoby przed scaleniem.
- Komunikaty commitów piszemy po angielsku, w trybie rozkazującym i opisowo: `Add spatial query for nearest stations`, a nie `update` ani `poprawki`.
- PR scalamy przyciskiem **„Create a merge commit"** (nie „Squash"), żeby w historii zostały pojedyncze commity.

## Jednorazowa konfiguracja

```bash
git clone <adres-repozytorium>
cd <katalog-repozytorium>

git config user.name "Imię Nazwisko"
git config user.email "adres-email-przypisany-do-konta-GitHub"
```

Adres e-mail musi być tym samym, który jest dodany do Twojego konta GitHub. Inaczej commity nie będą przypisane do Ciebie i nie pokażą się w Twoim wkładzie w projekt.

## Praca krok po kroku

### 1. Weź zadanie z tablicy

Otwórz tablicę projektu (zakładka **Projects** w repozytorium), wybierz z kolumny `Todo` zadanie, do którego jesteś przypisany(-a) i przenieś kartę do `In Progress`.

### 2. Załóż branch

Najłatwiej z poziomu issue: po prawej stronie, w sekcji **Development**, kliknij **Create a branch**. Zostaw proponowaną nazwę (zawiera numer issue, np. `12-import-gtfs`) i wybierz źródło `main`. Potem u siebie:

```bash
git fetch origin
git checkout 12-import-gtfs
```

Ręcznie (jeśli wolisz):

```bash
git checkout main
git pull
git checkout -b 12-import-gtfs
```

Nazwa brancha: `<numer-issue>-krotki-opis`, małymi literami, z myślnikami.

### 3. Pracuj i commituj

Commituj często, małymi kawałkami, które mają sens:

```bash
git status
git add <konkretne-pliki>
git commit -m "Add GTFS import script"
```

Przed `git add` sprawdź `git status`, żeby nie dodać plików, których nie chcesz (`.env`, pliki IDE, `node_modules/`). Większość z nich blokuje `.gitignore`, ale lepiej zerknąć.

### 4. Zaktualizuj branch przed PR-em

Jeśli ktoś w międzyczasie scalił coś do `main`, pobierz zmiany do swojego brancha i rozwiąż ewentualne konflikty:

```bash
git fetch origin
git merge origin/main
```

Uruchom testy lokalnie (jeśli są dla Twojej części).

### 5. Wypchnij branch i otwórz pull request

```bash
git push -u origin 12-import-gtfs
```

Na GitHubie kliknij **Compare & pull request** i uzupełnij szablon:

- base: `main`,
- w opisie wpisz `Closes #12` (numer Twojego issue). Po scaleniu PR issue zamknie się samo, a karta przejdzie do `Done`,
- w **Reviewers** ustaw osobę z Twojej pary (patrz niżej),
- w **Assignees** ustaw siebie,
- przenieś kartę zadania na tablicy do `In Review`.

### 6. Przegląd

Recenzent czyta zmiany, komentuje i klika **Approve** albo **Request changes**. Autor poprawia na tym samym branchu (nowe commity i `git push`), PR aktualizuje się sam.

### 7. Scalanie

Po zatwierdzeniu autor klika **Create a merge commit**, a potem **Delete branch**. Lokalnie:

```bash
git checkout main
git pull
git branch -d 12-import-gtfs
```

## Pary do przeglądu

| Autor      | Recenzent  |
| ---------- | ---------- |
| Dominika   | Michał     |
| Michał     | Dominika   |
| Weronika   | Małgorzata |
| Małgorzata | Weronika   |

Jeśli PR dotyka czyjejś części (np. zmiana w bazie, z której korzysta API), dodaj też tę osobę jako recenzenta.

## Tablica zadań

- Kolumny:
  - `Backlog`: pomysły i zadania opcjonalne, jeszcze niezaplanowane,
  - `Todo`: zaplanowane, czekają na osobę,
  - `In Progress`: ktoś pracuje, jest branch,
  - `In Review`: otwarty PR czeka na przegląd,
  - `Done`: scalone (karta przechodzi tu po zamknięciu issue).
- Każde zadanie ma przypisaną osobę. Status zmieniaj na bieżąco, bo harmonogram jest oceniany.
- Brakuje zadania? Załóż issue z szablonu **Task**, a Małgorzata doda je do tablicy i harmonogramu.
- Etykiety określają obszar: `baza`, `qgis`, `api`, `frontend`, `ci`, `docs`.

## Styl kodu

- Python: PEP 8, `snake_case` dla funkcji i zmiennych, `CamelCase` dla klas.
- Znaczące nazwy (nie `a1`, `temp`, `x`), krótkie funkcje z jedną odpowiedzialnością, podział na moduły.
- Komentarze wyjaśniają dlaczego, a nie co robi oczywista linijka.
- Bez zakomentowanego kodu i testowych `print`.

## Czego nie wrzucamy do repozytorium

- Plików `.env`, haseł, kluczy i danych logowania (zamiast tego `.env.example` bez wartości).
- Plików IDE (`.vscode/`, `.idea/`), `node_modules/`, dużych lub tymczasowych danych (miejsce na nie: `data/raw/`, ignorowane przez Git).

## Gdy coś pójdzie nie tak

Nie używaj `git push --force` i nie kasuj repozytorium. Napisz na grupie, co się stało, razem to naprawimy.
