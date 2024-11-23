mkdir -p ./output

cp -frv ./config ./output/config
cp -frv ./.github ./output/.github
cp -frv ./.gitlab ./output/.gitlab
cp -frv ./.gitlab-ci.yml ./output/.gitlab-ci.yml
cp -frv ./rn_issue_auto_archiving ./output/rn_issue_auto_archiving

echo "output done"