@echo off
cd evolucao
for /l %%x in (1,1,1000) do (
echo Seed: %%x
python algoritmo.py %%x 1000
echo -------------------------------
)
PAUSE