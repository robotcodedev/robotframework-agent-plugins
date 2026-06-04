#!/usr/bin/env bash
# Test setup for the robotcode skill evals.
#
# Runs the demo suites so the results / diff / debugging evals have finished
# runs to analyze. Produces two runs under results/ (gitignored — output.xml
# embeds absolute paths):
#
#   results/baseline.xml  all tests pass (login forced good via -v PASSWORD)
#   results/output.xml    the default run, where 'Login Works' fails on purpose
#
# The failure in the current run is intentional: it's the planted regression the
# diff eval detects against the passing baseline. Run this once before the
# results-, diff-, and "debug from a recorded run" evals.
set -u
cd "$(dirname "$0")"

echo "==> baseline run (all passing)"
robotcode robot -v "PASSWORD:correct horse" --output baseline.xml --log NONE --report NONE \
  tests/login.robot tests/orders.robot

echo
echo "==> current run ('Login Works' fails on purpose)"
robotcode robot --output output.xml --log NONE --report NONE \
  tests/login.robot tests/orders.robot

echo
echo "Wrote results/baseline.xml (all pass) and results/output.xml (1 expected failure)."
echo "Try:  robotcode results summary --failed   |   robotcode results diff results/baseline.xml"
