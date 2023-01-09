PYTHON=python3
EXEC_DIR=$(pwd)
SAFTOOLS_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"



echo "cd ${SAFTOOLS_DIR}"
cd ${SAFTOOLS_DIR}

pwd

${PYTHON} -m safinfer "$@"

echo "cd ${EXEC_DIR}"
cd ${EXEC_DIR}