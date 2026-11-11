# Nettmagasin – GitHub Pages + Jekyll + redaksjonsagent

## Oppstart
1. Opprett et **offentlig** GitHub-repository, og last opp alle filene i denne mappen til `main` (inkludert `.github`).
2. Gå til **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Åpne **Actions** og kjør `Publish Jekyll site` manuelt første gang.
4. Åpne nettadressen som vises i Pages-deployeringen.
5. Endre `title`, `description`, `url` og `baseurl` i `_config.yml`. For `bruker.github.io/repo` brukes `url: "https://bruker.github.io"` og `baseurl: "/repo"`. For `bruker.github.io` brukes tom `baseurl`.

## Aktiver redaksjonsagenten (valgfritt – API koster normalt penger)
1. Opprett en OpenAI API-nøkkel med forbruksgrense.
2. GitHub → Settings → Secrets and variables → Actions → New repository secret: `OPENAI_API_KEY`.
3. Gi GitHub Actions skrivetilgang: Settings → Actions → General → Workflow permissions → Read and write permissions.
4. Agenten forsøker kjøring mandag–fredag kl. 10 Europe/Oslo. Cron kjører 08:00 og 09:00 UTC, og skriptet velger korrekt Oslo-klokkeslett. GitHub-skjema kan bli forsinket.
5. Ekstraordinær sak: Actions → Redaksjonsagent → Run workflow → fyll inn emne **og kildelenker**.

## Redaksjonell sikkerhet og begrensninger
- Maks 3 ordinære artikler per dato, ingen garantert minimumspublisering.
- Ekstraordinære saker bruker eget filprefiks og teller ikke mot ordinær dagskvote.
- Ingen publisering uten minst to oppgitte kilder. Skriptet kan **ikke verifisere kildenes innhold**; dette er en grunnmur, ikke et fullverdig faktasjekksystem.
- Agenten kan velge å publisere null artikler. Det er forventet når dokumentasjonen er for svak.
- RSS-kilder er konfigurerbare via repository variable `RSS_FEEDS` (kommaseparerte URL-er). Standard er NRK toppsaker.
- Ekstraordinære saker trenger faktagrunnlag i kommandoen; kun et emne er ikke nok.
- For produksjon anbefales egen research-modul med faktisk kildeinnhenting og kildekontroll før automatisk publisering.
- `OPENAI_MODEL` kan settes som repository variable.
