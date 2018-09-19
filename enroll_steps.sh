# 1, Create a user profile, and get the profile id
python CreateProfile.py ccc2411ed1bb496fbc3aaf42540e81ac

# 2, Print all user profiles(to get current id)
python PrintAllProfiles.py ccc2411ed1bb496fbc3aaf42540e81ac

# 3, Enroll user profiles with provided wav files
python EnrollProfile.py ccc2411ed1bb496fbc3aaf42540e81ac 7874fb49-1c07-493c-b948-a496d6b1d1a9 ../data/kun.wav True

# 4, Identify test files from given ids with provided wav files
python IdentifyFile.py ccc2411ed1bb496fbc3aaf42540e81ac ../data/fankun_test.wav True fc9bc083-88a2-41f6-869e-ec20b3390c23 aabd9804-3c66-46d1-b8d3-4598b8aca4d8

# 5, delete profile
python DeleteProfile.py ccc2411ed1bb496fbc3aaf42540e81ac 6491f6ec-7f7e-4e6d-95d4-1020d227ec10

kai: aabd9804-3c66-46d1-b8d3-4598b8aca4d8, en-us, 36.37, 0.0, 2018-09-18T16:50:31.065Z, 2018-09-18T16:51:26.229Z, Enrolled
kun: 7874fb49-1c07-493c-b948-a496d6b1d1a9, en-us, 37.38, 0.0, 2018-09-18T16:54:40.925Z, 2018-09-18T16:56:57.707Z, Enrolled
chang:

