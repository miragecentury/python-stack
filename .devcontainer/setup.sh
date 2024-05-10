
# Install virtualenv and dependencies in it
poetry install --all-extras --with=test

# Install git cz tooling with the conventional-changelog
npm install -g cz-conventional-changelog
touch ~/.czrc && echo '{ "path": "cz-conventional-changelog" }' > ~/.czrc
