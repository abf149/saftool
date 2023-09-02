# Profiling process derived from
# https://medium.com/@narenandu/profiling-and-visualization-tools-in-python-89a46f578989

PYTHON=python3
EXEC_DIR=$(pwd)
SAFTOOLS_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"



echo "cd ${SAFTOOLS_DIR}"
cd ${SAFTOOLS_DIR}

pwd

${PYTHON} -m cProfile -o test.pstats safinfer.py "$@"
gprof2dot -f pstats test.pstats | dot -Tpng -o safinfer_prof.png

echo "cd ${EXEC_DIR}"
cd ${EXEC_DIR}