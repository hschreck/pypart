require 'optparse'
require 'fileutils'

# Option parser to call script from command line
## Options struct to contain geometry, size, and primary partition designation
Options = Struct.new(:geometry, :size, :primary, :device)

options = Options.new("#{FileUtils.pwd()}/sda-pt.sf", 1000000000, 2, "/dev/sda")
OptionParser.new do |opts|

  opts.banner = "Usage: resize.rb [options]"

  opts.on("-g", "--geometry FILEPATH", "Use specificed geometry file") do |sf|
    options.geometry = sf
  end

  opts.on("-s", "--size DISKSIZE", "Specify disk size in sectors") do |size|
    options.size = size
  end

  opts.on("-p", "--primary PARTNUM", "Specify primary partition by number") do |primary|
    options.primary = primary
  end

  opts.on("-d", "--device DEVICE", "Specify block device (ex. /dev/sda)") do |device|
    options.device = device
  end
end.parse!


geometryFile = File.readlines("#{options.geometry}")

#Starting at end of file, move back through partitions until primary partition
lineIndex = -1
partEnd = options.size.to_i
until geometryFile[lineIndex].include? "#{options.device}#{options.primary}"
  partSize = geometryFile[lineIndex].scan(/size= *\d*/)[0].split(" ")[1].to_i
  partStart = partEnd-partSize
  geometryFile[lineIndex].gsub!(/start= *\d*/, "start= #{partStart}")
  lineIndex -= 1
  partEnd = partStart
end

# generate primary partition specification and output full spec
partStart = geometryFile[lineIndex].scan(/start= *\d*/)[0].split(" ")[1].to_i
partSize = partEnd-partStart

geometryFile[lineIndex].gsub!(/size= *\d*/, "size=#{partSize}")

puts geometryFile
