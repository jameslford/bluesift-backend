




# class ConversionFormat:

#     def __init__(self, product: ProductSubClass, extension: str, file_type=None):

#         ref, alt_ftype = product.map_extension(extension)
#         self.reference = ref
#         self.extension = extension
#         self.filetype = file_type if file_type else alt_ftype
#         self.filename = product.name + self.extension
        # self.reference.save(self.filename, ContentFile(''))



    # def get_file_object(self):

        #     buffer = io.StringIO()
        #     req = requests.get(self.initial_file.url)
        #     buffer.write(req.text)
        #     buffer.seek(0)
        #     print(buffer)
        #     print(req.elapsed)
        #     req.close()
        #     return buffer
        # with requests.get(self.initial_file.url, stream=True) as req:
        #     with io.BytesIO() as buffer:
        #         for chunk in req.iter_content(80111, True):
        #             if chunk:
        #                 buffer.write(chunk)
        # buffer.seek(0)
        # req.close()
        # return buffer

        # if not os.path.exists('temp'):
        #     os.mkdir('temp')

        # with requests.get(self.initial_file.url, stream=True) as r:
        #     with open(self.initial_local_filename, 'wb') as f:
        #         for chunk in r.iter_content(800111, True):
        #             if chunk:
        #                 f.write(chunk)
        # r.close()
        # f.close()
        # buffer = io.BytesIO()

        # print(r.elapsed)
        # obj = PipAssimp.load(self.initial_local_filename, 'obj')

        # for ftype in self.conversion_formats:
        #     PipAssimp.export(
        #         obj,
        #         'temp/' + ftype.filename,
        #         ftype.filetype,
        #         )
        #     temp_files = os.listdir('temp')
        #     for cwd_file in temp_files:
        #         if self.product.name in cwd_file:
        #             cwd_extension = '.' + cwd_file.split('.')[-1]
        #             reference = self.product.map_extension(cwd_extension)
        #             if not reference:
        #                 print(cwd_file + ' has invalid extension')
        #                 continue
        #             print(cwd_file + ' has valid extension')
        #             local_path = 'temp/' + cwd_file
        #             file = open(local_path, 'rb')
        #             ftype.reference.save(cwd_file, File(file), save=True)
        #             file.close()
        #             os.remove(local_path)
        #     os.remove(self.initial_local_filename)
        # PipAssimp.release(obj)
        # self.product.save()

