---
subject: Gaming/DnD
tags: [dnd, courts-of-the-shadow-fey, kobold-press, dm-tools, python, status-mechanics, rp-module]
created: 2026-05-19
source: Perplexity
---

# Courts Of The Shadow Fey Module

## Summary
Detailed breakdown of the Courts of the Shadow Fey module by Kobold Press, a roleplay-heavy political intrigue adventure for levels 7-10. Includes a Python DM Manager tool for tracking 5-10 characters, the Status mechanic system, faction dynamics, and three recommended campaign pathways.

## Key Points
- Courts of the Shadow Fey by Kobold Press is a 5e-compatible adventure designed for levels 7-10, divided into four acts playing like TV seasons
- Python DM Manager tool (shadow_fey_manager.py) supports 5-10 characters at levels 5-6 with HP, AC, conditions, faction tracking, and session history logging
- Status system is the core RP mechanic: base equals Charisma modifier, minus 2 for non-fey races, plus titular bonuses (Knight +1, Lord/Lady +2, Duke/Duchess +4, King/Queen +8)
- Status gain/loss actions from Tables 22/23 are built into the tool (e.g., defeating monolith footman +1, insulting Blood Royal minus 7)
- Privilege thresholds: Status 11 unlocks Revich audience, Status 26 unlocks Queen's audience
- Four factions: Ravens (+1 Status, magic weapon reward), Grey Ladies (+4 Status but costs 10 max HP or a spell slot), Lords of Light (+1 Status, grants halo note), Akyishigal (+2 Status, adds roach companion)
- Act I (A Chill in the Air): Zobeck investigation, stopping assassins, confronting Hidden Ambassador Thelamandrine, learning the Shadow Road ritual
- Act II (The Invisible Courts): Lower Halls and Winter Palace, Status-based illusion gating, faction joining, Status 11+ unlocks upper court access
- Act III (The Honored Guests): Royal Halls, political drama and romance and formal duels, courtesan wooing (Table 32), dueling season, Akyishigal recruitment, Firebird Hunt, Status 20+ qualifies for Queen audience
- Act IV (Royal Audiences and Treachery): Spiral Maze and Tower of the Moon, audience with Queen Sarastra, labyrinth challenges, Tower of the Moon climb, final confrontation with the Moonlit King (skill challenge or combat)
- Final choice: keep the Orb of Rule, give to Akyishigal (dark outcome), or give to Queen (restore control and free Zobeck)
- Courtesan and consort wooing uses full Table 32 with minimum Status checks, skill challenges, and Status bonus on success or minus 2 penalty on failure
- Status gifting (blood oath): gifting Status permanently reduces giver's max HP (1-2 Status costs 5 max HP, unreclaimable for 1 year and a day)
- Long rest costs 1 week in the Shadow Realm
- Three campaign pathways: Heroic Diplomats (high RP, low grimness), Dark Court Operatives (intrigue and moral corruption), Status Ladder (mechanically tight, Status as central game loop)
- Dice roller handles any standard notation, group/individual initiative, per-character damage and healing and condition management
- Full JSON save/load for persisting party state between sessions

## Details
The Status system is the defining mechanic of Courts of the Shadow Fey. Unlike traditional D&D where combat progression drives the narrative, Status determines what doors open, who will speak to the party, and what areas are even visible (low-Status characters see the Courts as empty or abandoned due to illusion cloaking).

The Python DM Manager integrates all PDF mechanics into an interactive console. It tracks Status gains and losses from each act's scenes, runs skill challenges for Shadow Road ritual research, faction joins, courtesan wooing, and the Moonlit King mind-restoration. It also handles duels, initiative, and damage during Dueling Season encounters.

The three campaign pathways offer distinct tones. The Heroic Diplomats route emphasizes negotiation, wit, and moral choices, steering players toward the Lords of Light and away from dark factions. The Dark Court Operatives route encourages risky Status gains, Akyishigal recruitment, and morally ambiguous choices leading to a dark epilogue. The Status Ladder route makes the Status system the explicit central game loop, with every scene framed in terms of Status gains and losses.

## References
- Kobold Press: Courts of the Shadow Fey module
- pdfcoffee.com: Courts of the Shadow Fey PDF reference
- No external references.

## Related
- [[DnD-Hub]]
- [[Curse Of Strahd Campaign Notes]]
- [[Dark Gothic Horror Campaign Creation]]
- [[Aethoria-Geography-And-Climate]]
