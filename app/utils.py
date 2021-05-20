import os, sys, time
import threading
import getopt, glob
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

def audioFileExists(fil):
    return os.path.isfile(fil)


class AudioConverter:

    def __init__(self):
        self.inputDir =  "./app/uploads"
        self.inputFormat = ""
        self.outputDir = "./app/converted"
        self.outputFormat = ""
        self.error_message = ""
        self.encoders = {"mp3": "lame", "wav": "wavenc", "aac": "avenc_aac", "ogg": "vorbisenc"}
        self.supportedOutputFormats = self.encoders.keys()
        self.supportedInputFormats = ("ogg", "mp3", "wav", "aac")

        self.pipeline = None
        self.is_playing = False
        self.processArgs()
        self.constructPipeline()
        self.connectSignals()
    
    def constructPipeline(self):
        self.pipeline = Gst.Pipeline("pipeline")
        self.filesrc = Gst.ElementFactory.make("filesrc")
        self.decodebin = Gst.ElementFactory.make("decodebin")
        self.audioconvert = Gst.ElementFactory.make("audioconvert")
        self.filesink = Gst.ElementFactory.make("filesink")
        encoder_str = self.encoders[self.outputFormat]
        self.encoder = Gst.ElementFactory.make(encoder_str)

        self.pipeline.add(self.filesrc, self.decodebin,
                          self.audioconvert, self.encoder,
                          self.filesink)
        # Link elements in the pipeline.
        # Gst.element_link_many(self.filesrc, self.decodebin)
        self.filesrc.link(self.decodebin)
        # Gst.element_link_many(self.audioconvert, self.encoder, self.filesink)
        self.audioconvert.link(self.encoder)
        self.encoder.link(self.filesink)
    
    def connectSignals(self):
        """
        Connect various signals with the class methods.
        """
        # Connect the signals. ( catch the messages on the bus )
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin "pad_added" signal.
        self.decodebin.connect("pad_added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        audioconvert, when the decodebin element generated "pad_added" signal
        """
        caps = pad.query_caps(None)
        compatible_pad = self.audioconvert.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def processArgs(self):
        """
        Process the command line arguments. Print error and the usage
        if there is an error processing the user supplied arguments.
        """
        # Process command line arguments
        args = sys.argv[1:]
        shortopts = ''
        longopts = ['input_dir=', 'input_format=',
                    'output_dir=', 'output_format=']
        try:
            opts, args = getopt.getopt(args, shortopts, longopts)
        except getopt.GetoptError as error:
            # print usage
            self.printUsage()
            # print the error message and exit.
            sys.exit(error)

        if not len(opts):
            self.printUsage()
            sys.exit(2)

        for opt, val in opts:
            print(opt)
            if opt == "--input_dir":
                assert os.path.exists(val)
                self.inputDir = os.path.normpath(val)
            elif opt == "--output_dir":
                assert os.path.exists(val)
                self.outputDir = os.path.normpath(val)
            elif opt == "--input_format":
                format = val
                format = format.lower()
                assert format in self.supportedInputFormats
                self.inputFormat = val
            elif opt == "--output_format":
                format = val
                format = format.lower()
                assert format in self.supportedOutputFormats
                self.outputFormat = val

        # Now check if output directory has been specified. If not, create one.
        if not self.outputDir:
            pth = os.path.join(self.inputDir, 'OUTPUT_AUDIOS')
            if not os.path.exists(pth):
                os.makedirs(pth)
            self.outputDir = pth

        if not self.outputFormat:
            print("\n Output audio format not specified."
                  "Saving audio file in the default \"mp3\" format.")
            self.outputFormat = "mp3"

    def printUsage(self):
        print("\n Audio converter usage:")
        print("\n python AudioConverter [options]")
        print("\n The [options] are:")
        print(" \n"
              "--input_dir   : The directory from which to read the input audio file(s) to "
              "\nbe converted"
              "\n--input_format: The audio format of the input files. The format should be "
              "\n in a supported list of formats. The supported formats are "
              "\n \"mp3\", \"ogg\" and  \"wav\". If no format is specified, "
              "\n it will use the default format as \".wav\" ."
              "\n --output_dir   : The output directory where the converted files will be saved "
              "\n --output_format: The audio format of the output file. Should be in the "
              "\n  supported formats are \"wav\" and \"mp3\". If no format is specified, "
              "\n it will use \"mp3\" as the default output format")

    def printFinalStatus(self, inputFileList, starttime, endtime):
        """
        Print the final status of audio conversion process.
        """
        print("inputFileList niye None geliyor?", inputFileList, starttime, endtime)

        if self.error_message:
            print(self.error_message)
        else:
            print("\n Done!")
            print("\n {} audio(s) written to directory: {}".format(len(inputFileList), self.outputDir))
            print("\n Approximate time required for conversion: {} seconds".format(endtime - starttime))

    def convert(self):
        """
        Convert the input audio files into user specified audio format.
        @see: self.convert_single_audio()
        """
        pattern = "*." + self.inputFormat
        filetype = os.path.join(self.inputDir, pattern)
        fileList = glob.glob(filetype)
        print("fileList Ney?:", fileList)

        inputFileList = filter(audioFileExists, fileList)
        print("inputFileList Ney?:", inputFileList)

        # iter = (i for i in range(50))
        # sum(1 for _ in iter)

        input_file_list = [x for x in inputFileList] # burada liste çevirmezsek lenght bulamıyor

        print("input_file_list_as_list Ney?:", input_file_list)

        if not len(input_file_list):
            print("\n No audio files with extension %s located"
                  "in dir %s") % (self.outputFormat, self.inputDir)
            return
        else:
            # Record time before beginning audio conversion
            starttime = time.clock()
            print("\n Converting Audio files..")

        # Save the audio into specified file format.
        # Do it in a for loop
        # If the audio by that name already
        # exists, do not overwrite it OR define and use
        # flag -f to decide whether to overwrite it!

        for inPath in input_file_list:
            print("number_of_files", inPath)
            dir, fil = os.path.split(inPath)
            print(" burayı pas mı geçiyor kancık ? :", dir, fil)
            fil, ext = os.path.splitext(fil)
            print(" burayı pas mı geçiyor kancık ? :", fil, ext)

            outPath = os.path.join(self.outputDir, fil + "." + self.outputFormat)
            # Following check is already done.
            # if not self.encoders.has_key(ext):
            # print " Invalid extension ", ext

            print("\n Input File: %s%s, Conversion STARTED..." % (fil, ext))
            self.convert_single_audio(inPath, outPath)
            if self.error_message:
                print("\n Input File: %s%s, ERROR OCCURED." % (fil, ext))
                print(self.error_message)
            else:
                print("\n Input File: %s%s, Conversion COMPLETE " % (fil, ext))

        endtime = time.clock()

        self.printFinalStatus(input_file_list, starttime, endtime)
        evt_loop.quit()

    def convert_single_audio(self, inPath, outPath):
        """
        Convert a single audio file and save it.
        @param inPath: Input audio file path
        @type inPath: string
        @param outPath: Output audio file path
        @type outPath: string
        """
        # @NOTE: The following applies mainly for Windows platform.
        # The inPath is obtained from the 'for loop'. The os.path.normpath
        # doesn't work on this string. Gstreamer will throw error processing
        # such path
        # One way to handle this is to use repr(string) , which will return the
        # whole string including the quotes .
        # For example: if inPath = "C:/AudioFiles/my_music.mp3"
        # repr(inPath) will return "'C:\\\\AudioFiles\\\\my_music.mp3'"
        # We will need to get rid of the extra single quotes at the beginning
        # and end by slicing the string as  inPth[1:-1]
        inPth = repr(inPath)
        outPth = repr(outPath)

        # Set the location property for file source and sink
        self.filesrc.set_property("location", inPth[1:-1])
        self.filesink.set_property("location", outPth[1:-1])

        self.is_playing = True
        self.pipeline.set_state(Gst.State.NULL)
        while self.is_playing:
            time.sleep(1)

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == Gst.MessageType.ERROR:
            self.pipeline.set_state(Gst.State.NULL)
            self.is_playing = False
            print("\n Unable to play audio. Error: ", message.parse_error())
        elif msgType == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            self.is_playing = False

# Init Gstreamer
Gst.init(None)

# Run the program
converter = AudioConverter()
# thread.start_new_thread(player.play, ())
thread = threading.Thread(target=converter.convert)
thread.start()
GObject.threads_init()
evt_loop = GObject.MainLoop()
evt_loop.run()