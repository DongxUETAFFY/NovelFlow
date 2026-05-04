#!/usr/bin/env bash
# Validate summaries.md first-sentence quality for English or Chinese novels.
#
# The first sentence of every chapter summary feeds the pyramid compression
# pipeline. When a chapter is 80 chapters in the past, Tier 5 is exactly this
# sentence. Vague first sentences silently destroy narrative memory.
#
# Checks each summary against the First Sentence Rule (prose-guide.md):
#   1. Named character (who acted or was acted upon)
#   2. Concrete event (what specifically happened)
#   3. Directional consequence (why it matters to what comes next)
#
# Heuristics proxy for these three requirements:
#   - Too short to carry all three parts -> WARN
#   - Vague verb patterns -> FAIL
#   - No known character name or name-like token -> WARN
#   - No consequence marker -> WARN
#
# Usage:
#   ./scripts/validate-summaries.sh [novel/summaries.md] [novel/characters.md]

set -euo pipefail

SUMMARIES="${1:-novel/summaries.md}"
CHARACTERS="${2:-$(dirname "$SUMMARIES")/characters.md}"

if [ ! -f "$SUMMARIES" ]; then
    echo "ERROR: $SUMMARIES not found."
    echo "Run novel-setup first to create the novel/ directory, then write some chapters."
    exit 1
fi

echo "=== Summary First-Sentence Quality Check ==="
echo "File: $SUMMARIES"
if [ -f "$CHARACTERS" ]; then
    echo "Characters: $CHARACTERS"
else
    echo "Characters: (not found, using weaker name heuristic)"
fi
echo ""

awk -v characters_file="$CHARACTERS" '
BEGIN {
    fails = 0
    warns = 0
    passes = 0

    vague_en = "(continues|deals with|experiences|goes through|begins to|starts to|tries to|seems to|becomes|feels|thinks about|reflects on|considers|wonders about)"
    vague_zh = "(继续|处理|经历|开始|试图|似乎|变得|感觉|思考|反思|考虑|关系推进|矛盾升级|气氛紧张|局势变化)"
    consequence_en = "(but|because|therefore|so|while|forcing|leaving|revealing|causing|which|as a result)"
    consequence_zh = "(但|却|因此|所以|从而|导致|迫使|使得|让|暴露|揭示|埋下|推动|转向|加速|恶化|改变|确认|失去|获得|无法|必须)"

    if (characters_file != "" && (getline line < characters_file) >= 0) {
        do {
            candidate = ""
            if (line ~ /^## /) {
                candidate = line
                sub(/^##[[:space:]]*/, "", candidate)
                sub(/[（(].*$/, "", candidate)
                sub(/[[:space:]].*$/, "", candidate)
            } else if (line ~ /\*\*[^*]+\*\*/) {
                candidate = line
                sub(/^[^*]*\*\*/, "", candidate)
                sub(/\*\*.*$/, "", candidate)
                sub(/[（(].*$/, "", candidate)
            }
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", candidate)
            if (candidate != "" && candidate !~ /角色|Character|Relationships|关系/) {
                names[++name_count] = candidate
            }
        } while ((getline line < characters_file) > 0)
        close(characters_file)
    }
}

/^##[[:space:]]+(Chapter|第)/ {
    if (chapter != "") { output_summary() }
    chapter = $0
    sub(/^##[[:space:]]*/, "", chapter)
    title = ""
    if (index($0, ":") > 0) {
        title = substr($0, index($0, ":") + 2)
    } else if (index($0, "：") > 0) {
        title = substr($0, index($0, "：") + 1)
    }
    next
}
/^##[[:space:]]+/ { next }
/^$/ { next }
chapter != "" && first_sentence == "" && length($0) > 0 {
    line = $0
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
    if (match(line, /[。！？.!?]/)) {
        first_sentence = substr(line, 1, RSTART)
    } else {
        first_sentence = line
    }
    next
}
{ next }
function output_summary() {
    if (first_sentence == "") { first_sentence = "(empty — summary not yet written)" }
    validate_summary(chapter, title, first_sentence)
    first_sentence = ""
}
function validate_summary(ch, title, first,    compact, result, reason, i, has_name, has_cjk, has_latin_name, has_vague, has_consequence, token_count, tmp_words) {
    compact = first
    gsub(/[[:space:]]/, "", compact)

    has_name = 0
    for (i = 1; i <= name_count; i++) {
        if (names[i] != "" && index(first, names[i]) > 0) {
            has_name = 1
            break
        }
    }
    has_cjk = first ~ /[一-龥]/
    has_latin_name = first ~ /[A-Z][a-z]+/
    has_vague = (tolower(first) ~ vague_en || first ~ vague_zh)
    has_consequence = (tolower(first) ~ consequence_en || first ~ consequence_zh)

    result = "PASS"
    reason = ""

    if (has_vague) {
        result = "FAIL"
        reason = append_reason(reason, "vague event language")
    }
    if (!has_name && !has_latin_name) {
        result = max_result(result, "WARN")
        reason = append_reason(reason, "no known character name detected")
    }
    if ((has_cjk && length(compact) < 18) || (!has_cjk && split(first, tmp_words, /[[:space:]]+/) < 10)) {
        result = max_result(result, "WARN")
        reason = append_reason(reason, "too short to carry event + consequence")
    }
    if (!has_consequence) {
        result = max_result(result, "WARN")
        reason = append_reason(reason, "no clear directional consequence marker")
    }

    if (result == "FAIL") { fails++ }
    else if (result == "WARN") { warns++ }
    else { passes++ }

    printf "  %-18s [%4s]  %s\n", ch, result, first
    if (reason != "") {
        printf "                    (reason: %s)\n", reason
    }
}
function append_reason(reason, addition) {
    if (reason == "") { return addition }
    return reason "; " addition
}
function max_result(current, candidate) {
    if (current == "FAIL" || candidate == "FAIL") { return "FAIL" }
    if (current == "WARN" || candidate == "WARN") { return "WARN" }
    return "PASS"
}
END {
    if (chapter != "") { output_summary() }
    total = fails + warns + passes
    print ""
    print "=== Results ==="
    printf "  PASS: %d / %d\n", passes, total
    printf "  WARN: %d / %d\n", warns, total
    printf "  FAIL: %d / %d\n", fails, total
    print ""

    if (total == 0) {
        print "No chapter summaries found yet."
    } else if (fails > 0 || warns > 0) {
        print "Action needed:"
        print "  FAIL - rewrite first sentence with: named character + concrete event + directional consequence"
        print "  WARN - review first sentence; may be too compressed to survive pyramid tier collapse"
        print ""
        print "Good examples:"
        print "  \"Kira identifies the mole as her own partner, forcing her to choose between the case and her cover.\""
        print "  \"林夜在审讯室折断嫌犯手臂，导致沈鸢确认他的失控已从异界蔓延到现实。\""
        print "Bad examples:"
        print "  \"The investigation continues and tensions rise.\""
        print "  \"林夜继续处理案件，局势变得紧张。\""
    }

    if (fails > 0) { exit 1 }
}
' "$SUMMARIES"
