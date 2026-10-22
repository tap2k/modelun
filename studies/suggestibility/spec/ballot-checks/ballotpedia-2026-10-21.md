# Ballotpedia cross-check of ballot-races-2026.json

Checked 2026-10-21 against Ballotpedia per-state House and Senate 2026 pages, all 50 states, all 443 races. WebFetch returned empty pages for ballotpedia.org (bot protection), so pages were downloaded with curl and a browser user-agent and read as text.

Counts: 57 mismatches (55 incumbent coding, 1 same-party/extra-candidate race, 1 missing eligible race, 0 D/R name mismatches); 2 surname spelling differences; 0 states unverified.

Pattern: every California, Washington and Alaska House row has an empty incumbent field. These are the top-two/top-four states, so the Wikipedia parse probably did not read incumbency from their tables. WA-4 (Newhouse not on ballot) and CA-26, CA-38, CA-48 are correctly open.

## 1. Mismatches

| race id | field | list value | Ballotpedia value | Ballotpedia URL |
|---|---|---|---|---|
| house-CA-1 | incumbent | (empty) | R (James Gallagher; LaMalfa did not make the ballot) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-2 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-3 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-5 | incumbent | (empty) | R | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-8 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-9 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-10 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-13 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-15 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-16 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-17 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-18 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-19 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-20 | incumbent | (empty) | R | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-21 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-22 | incumbent | (empty) | R | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-23 | incumbent | (empty) | R | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-24 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-25 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-27 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-28 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-30 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-31 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-32 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-33 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-35 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-36 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-39 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-41 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-42 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-43 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-44 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-45 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-46 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-47 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-49 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-50 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-51 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-CA-52 | incumbent | (empty) | D | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_California,_2026 |
| house-AK-AL | incumbent | (empty) | R (Nick Begich) | https://ballotpedia.org/United_States_House_of_Representatives_election_in_Alaska,_2026 |
| senate-AK | one D and one R | D Mary Peltola, R Dan Sullivan | Top-four general has two Republicans: Dan S. Sullivan (R, incumbent) and Gerald Heikes (R, advanced after David Leslie (D) withdrew). Also Daniel J. Sullivan Jr. (No Party Affiliation), so two candidates share the surname Sullivan. | https://ballotpedia.org/United_States_Senate_election_in_Alaska,_2026 |
| house-TX-18 | incumbent | (empty) | D (Christian Menefee, incumbent; beat Al Green in the D runoff) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Texas,_2026 |
| house-TX-25 | incumbent | (empty) | R (Roger Williams) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Texas,_2026 |
| house-TX-37 | incumbent | (empty) | D (Greg Casar) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Texas,_2026 |
| house-OK-3 | missing race | (not in list) | D Suzie Byrd vs R Frank Lucas (incumbent R); exactly one D and one R | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Oklahoma,_2026 |
| house-AL-2 | incumbent | (empty) | D (Shomari Figures, incumbent, running) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Alabama,_2026 |
| house-NC-11 | incumbent | R | open. Chuck Edwards (R) won the primary, withdrew in August after a House Ethics report; district GOP chose Jennifer Balkcom 2026-08-10. R=Balkcom in the list is right. | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_North_Carolina,_2026 |
| house-WA-1 | incumbent | (empty) | D (Suzan DelBene) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-WA-2 | incumbent | (empty) | D (Rick Larsen) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-WA-3 | incumbent | (empty) | D (Marie Gluesenkamp Perez) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-WA-5 | incumbent | (empty) | R (Michael Baumgartner) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-WA-6 | incumbent | (empty) | D (Emily Randall) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-WA-7 | incumbent | (empty) | D (Pramila Jayapal) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-WA-8 | incumbent | (empty) | D (Kim Schrier) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-WA-9 | incumbent | (empty) | D (Adam Smith) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-WA-10 | incumbent | (empty) | D (Marilyn Strickland) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Washington,_2026 |
| house-UT-4 | incumbent | (empty) | R (Mike Kennedy, moved from old UT-3 under the new map; list codes Moore UT-2 and Maloy UT-3, who also moved, as R) | https://ballotpedia.org/United_States_House_of_Representatives_elections_in_Utah,_2026 |

## 2. Surname spelling differences

- house-KY-3 R: list "Maria Rodriquez", Ballotpedia "Maria Teresa Rodriguez"
- house-NY-9 R: list "Joel Azumah", Ballotpedia "Joel Anabilah-Azumah"

Same-surname variants a strict string matcher could trip on (not mismatches):
- house-GA-10 D: list "Pam Delancy", Ballotpedia "Pamela DeLancy" (capitalization)
- house-FL-26 R: list "Díaz-Balart", Ballotpedia "Diaz-Balart" (accent)
- house-FL-28 R: list "Giménez", Ballotpedia "Gimenez" (accent)
- house-MI-13 R: list value "T.&nbsp;P. Nykoriak" contains a literal HTML entity from the parse; Ballotpedia "Taras Nykoriak"

Different first name, same surname (same person per sources): house-NY-13 R "Jomo Williams" vs Ballotpedia "Manual Williams" (Manual "Jomo" Williams); house-TX-12 D "Angela Rodriguez Prilliman" vs "Heli Rodriguez Prilliman"; house-FL-24 R "Te Mayonna Brown" vs "Tedora Brown". Ordinary nickname and middle-initial variants are listed in the per-group files under parts/.

## 3. Not verified

None. Every state was checked against its state-level page. Per-district pages often returned HTTP 202 with no body, so they were not used for a second check. NC-11 was confirmed from the state page plus NC Newsline and Roll Call (2026-08-10).

## Notes: changes the list already reflects correctly

- senate-ME: Graham Platner (D) withdrew 2026-07-10; convention chose Troy Jackson 2026-07-25.
- senate-SC: Lindsey Graham died 2026-07-11; Darline Graham was appointed and won the GOP special runoff 2026-08-25; R=Darline Graham, inc=R correct.
- senate-NE: D nominee Cindy Burbank withdrew 2026-07-17; no D on the ballot, Osborn as nonpartisan.
- senate-SD: Julian Beaudion (D) withdrew; Rounds vs Bengs.
- senate-MT: Daines withdrew 2026-03-04; open; independent Seth Bodnar is also on the ballot.
- senate-TX open (Cornyn lost runoff to Paxton); senate-OK open (Mullin resigned March 2026).
- Correct open seats after primary losses: FL-7 (Mills), GA-13 (Blair), CO-1 (DeGette), KY-4 (Massie), NY-10 (Goldman), NY-13 (Espaillat).
- Correctly absent (no R or no D nominee, or excluded): PA-3, WI-2, FL-10, NJ-8, MA-1, MA-2, MA-5, MA-7, AZ-3 (R write-in only), CA-4, 6, 7, 11, 12, 14, 29, 34, 37, 40.
- Write-ins also listed: senate-NJ Eduardo Castillo (D), senate-ME Olson and Webb (D), senate-MN Alycia Gruenhagen (R).

## 4. Governor races (35, ballot-races-governor-2026.json)

Checked 2026-10-21 against Ballotpedia "<State> gubernatorial election, 2026" pages, fetched with curl. For IL, KS, MD, MN, OH and SD the page is titled "<State> gubernatorial and lieutenant gubernatorial election, 2026". Alaska is excluded as intended.

Counts: 0 mismatches, 0 surname spelling differences, 0 states unverified.

### Mismatches

None. All 35 D and R nominees match the Ballotpedia general-election lists. All 35 incumbent codings match. Incumbents are marked "Incumbent" in Ballotpedia's general-election sentence, or underlined in the candidate list for ID and TX. Inc=R is correct for AR, ID, NE, NV, NH, SD, TX and VT. Inc=D is correct for AZ, CT, HI, IL, MD, MA, NY, OR and PA. The other 18 are open seats, where Ballotpedia says "There are no incumbents in this race" or the sitting governor is not on the ballot (RI: McKee).

No D or R nominee has withdrawn or been replaced. The withdrawn or disqualified candidates Ballotpedia lists are all third-party or independent, for example GA Chase Oliver (L) and IA Nicholas Gluba (L).

### Surname spelling differences

None. Given-name variants only: GA Keisha Lance Bottoms / Keisha Bottoms; HI Josh / Joshua Green; ME Robert B. Charles / Bobby Charles; MA Mike / Michael Minogue; NM Deb / Debra Haaland; WY Kenneth / Ken Casner.

### Notes

- AL: open seat. Tuberville (R) is a senator, not the incumbent governor. The ballot also has a write-in independent, Ronald Burnette Jr.
- ME: Randy Wilcox is a Republican write-in alongside nominee Bobby Charles. AZ has two Republican write-ins (Gertritrude Gonzalez, Alice Novoa). FL has two no-party tickets with Republican lieutenant-governor running mates. None changes the D or R nominee.
