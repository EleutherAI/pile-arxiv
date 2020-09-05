from utils import *
import magic
mime = magic.Magic(mime=True)
import re


sh("mkdir -p tmp")

for dump in ls('files'):
    sh("rm -rf tmp/*")
    # extract
    print(dump)
    sh(f"tar xf {dump} -C tmp")

    for doc in lsr('tmp'):
        if doc.endswith('.gz'):
            sh(f"gunzip {doc}")
            type = mime.from_file(doc[:-3])
            print(type)
            if type == 'application/x-tar':
                sh(f"mkdir -p {doc[:-3]}_extract && tar xf {doc[:-3]} -C {doc[:-3]}_extract")
                sh(f"rm {doc[:-3]}")
            elif type == 'text/x-tex':
                sh(f"mv {doc[:-3]} {doc[:-3]}.tex")
            else:
                sh(f"rm {doc[:-3]}")

        elif doc.endswith('.pdf'):
            sh(f"rm {doc}")

    # process

    def tex_files():
        for doc in ls(ls('tmp')[0]):
            if os.path.isdir(doc):
                for name in ['main', 'Main', 'MAIN']: # common main file names
                    if os.path.exists(doc + '/' + name + '.tex'):
                        yield doc + '/' + name + '.tex'
                        break
                else:
                    if ls(doc) >> filt(X.endswith('.tex')) >> apply(len) == 1:
                        yield ls(doc) >> filt(X.endswith('.tex')) >> one()
                        continue
                    
                    # more than one top-level tex file, keep anything with \title
                    for titledoc in ls(doc) >> filt(X.endswith('.tex')):
                        if r'\title' in fread(titledoc):
                            yield titledoc
            elif doc.endswith('.tex'):
                yield doc

    texfiles = list(tex_files())
    for tex in texfiles:
        print(tex)
        out_name = tex.split('/')[2:] >> join('_') >> apply(X + '.md')

        try:
            sh(f'pandoc -s {tex} -o out/{out_name}')
        except ExitCodeError:
            import traceback
            traceback.print_exc()
            