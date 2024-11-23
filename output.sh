rm -rf ./output
mkdir -p ./output

cp -frv ./config ./output/config
cp -frv ./.github ./output/.github
cp -frv ./.gitlab ./output/.gitlab
cp -frv ./.gitlab-ci.yml ./output/.gitlab-ci.yml
cp -frv ./rn_issue_auto_archiving ./output/rn_issue_auto_archiving

rm -rf ./output/rn_issue_auto_archiving/__pycache__
rm -rf ./output/rn_issue_auto_archiving/auto_archiving/__pycache__
rm -rf ./output/rn_issue_auto_archiving/issue_processor/__pycache__
rm -rf ./output/rn_issue_auto_archiving/shared/__pycache__
rm -rf ./output/rn_issue_auto_archiving/utils/__pycache__

echo "output done"