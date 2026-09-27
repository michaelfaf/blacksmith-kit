<!--
Fill this in before door 1 (building a new skill) when nothing else hands the skill an approved plan. One page, filled by you, approved by you before drafting starts.
-->

# Plan card: <skill name>

## Goal
<!-- The goal in your own words, one to three sentences. What is this skill for? -->



## Done list
<!-- Each line provable by output: something a reader could point at and say "yes, that happened" or "no, it didn't." -->

-
-
-

## Plan
<!-- The steps the skill will take, in order, one line each: what it reads, what it does, what it produces. This is the plan the draft follows; nothing is re-asked after you approve it. -->

1.
2.
3.

## Where the build's paper goes
<!-- One folder for this build's brief and its test fixture, outside the skill folder. Default: a folder named builds/[skill name]/ in your workspace, with prompts/ and tests/ inside. -->



## Reads and writes
<!-- Every file or path this skill reads from and writes to. Be exact; a vague path here becomes a broken one later. -->

**Reads:**
-

**Writes:**
-

## Test prompts
<!-- Two to five real prompts, in your own words, that should make this skill fire and do the right thing. -->

1.
2.
3.

## Trigger phrases
<!-- The exact words you'd actually say to start this skill. -->

-
-

## The six flags
<!-- Answer yes or no. A "yes" adds that block to the skill; a "no" across all six means the skill stays as short as the base shape allows (the leaf rule). What each yes adds is in the blacksmith folder, references/standard.md § 2. -->

| Flag | Yes / No |
|---|---|
| F1: does it hand work to sub-agents? |  |
| F2: does it keep state outside its own folder? |  |
| F3: does it take an irreversible or costly action: money, a send, a write to a system of record, a publish? |  |
| F4: is the user in the loop turn by turn for the whole run? |  |
| F5: does it ship something to someone outside? |  |
| F6: does it run unattended or on a schedule? |  |

## Approval

Approved by the user on YYYY-MM-DD.
