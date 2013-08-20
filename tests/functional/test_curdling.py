import os

from datetime import datetime
from curdling import Curd, hash_files, get_curd, new_curd

from mock import patch


# Those are functional tests, I need to do some IO and all the files I have are
# located in the `fixtures` folder. The following line is just a shortcut to
# build absolute paths pointing to things inside of that folder.
FIXTURE = lambda *p: os.path.join(os.path.dirname(__file__), 'fixtures', *p)


def test_hashing_files():
    "It should be possible to get a uniq hash that identifies a list of files"

    # Given that I have a list of files and a mocked content for each one
    file_list = (
        FIXTURE('project1', 'requirements.txt'),
        FIXTURE('project1', 'development.txt'),
    )

    # When I hash them
    hashed = hash_files(file_list)

    # Then I see that the hash is right
    hashed.should.equal('284bf7a273bb72dd92e7d171fbd1dddceeb3eef3')


@patch('os.stat')
def test_has_curd(stat):
    "It should be possible to find curds saved locally"

    # Given that I have a curd hash and a path to a curdcache
    curd_id = 'my-curd'
    stat.return_value.st_ctime = 1376943600  # mocking the created prop

    # When I retrieve the unknown curd
    path = FIXTURE('project1', '.curds')
    curd = get_curd(path, curd_id)

    # Then I see that my curd was properly retrieved
    curd.should.be.a(Curd)
    curd.uid.should.equal('my-curd')
    curd.path.should.equal(path)
    curd.created.should.equal(datetime(2013, 8, 19, 16, 20))


def test_new_curd():
    "It should be possible to create new curds based on requirements files"

    # Given that I have a file that contains a list of dependencies of a fake
    # project
    requirements = (
        FIXTURE('project1', 'requirements.txt'),
        FIXTURE('project1', 'development.txt'),
    )
    uid = hash_files(requirements)

    # When I create the new curd
    path = FIXTURE('project1', '.curds')
    curd = new_curd(path, requirements)

    # Then I see the curd was downloaded correctly created
    os.path.isdir(FIXTURE('project1', '.curds')).should.be.true
    os.path.isdir(FIXTURE('project1', '.curds', uid)).should.be.true

    (os.path.isfile(FIXTURE('project1', '.curds', uid, 'pep8-1.4-py27-none-any.whl'))
        .should.be.true)
    (os.path.isfile(FIXTURE('project1', '.curds', uid, 'forbiddenfruit-0.1.0-py27-none-any.whl'))
        .should.be.true)