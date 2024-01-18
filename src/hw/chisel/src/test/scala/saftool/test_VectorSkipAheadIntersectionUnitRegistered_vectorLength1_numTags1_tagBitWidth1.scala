import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.freespec.AnyFreeSpec
import org.scalatest.flatspec.AnyFlatSpec
import scala.util.Random
import java.nio.file.{Files, Paths, StandardOpenOption}
import java.nio.charset.StandardCharsets
import scala.collection.mutable

class Workload_VectorSkipAheadIntersectionUnitRegistered(dut: VectorSkipAheadIntersectionUnitRegistered) extends PeekPokeTester(dut) {
  val rand = new Random

  // Accessing numTags and vectorLength from the component instance
  val numTags = dut.numTags
  val vectorLength = dut.vectorLength
  val maxTagValue = (1.2 * numTags).toInt // Retain existing calculation
  val checkOutputCorrectness = false // Flag to control output correctness checking

  // Function to generate a sorted list of unique random values
  def generateUniqueRandomList(size: Int, maxValue: Int): Seq[Int] = {
    val set = mutable.Set[Int]()
    while (set.size < size) {
      set += rand.nextInt(maxValue)
    }
    set.toSeq.sorted
  }

  // Generate unique test vectors
  val leftTestVector = generateUniqueRandomList(numTags, maxTagValue)
  val rightTestVector = generateUniqueRandomList(numTags, maxTagValue)

  // Step 1: Set pingpongSelect to 1 for writing to sub-buffer 0
  dut.io.pingpongSelect.poke(true.B)

  // Step 2: Write monotonically increasing test vectors to left and right memories
  dut.io.enable.poke(true.B)
  dut.io.left_writeEnable.poke(true.B)
  dut.io.right_writeEnable.poke(true.B)
  
  for (i <- leftTestVector.indices) {
    dut.io.left_writeData(i).poke(leftTestVector(i).U)
    dut.io.right_writeData(i).poke(rightTestVector(i).U)
  }

  // Allow time for writing to memories
  dut.clock.step(5)

  // Step 3: Set pingpongSelect to 0 to feed test vectors into DUT
  dut.io.pingpongSelect.poke(false.B)

  // Allow time for processing
  dut.clock.step(10)

  // Step 4: Set pingpongSelect to 1 for reading the result
  dut.io.pingpongSelect.poke(true.B)
  dut.io.readEnable.poke(true.B)

  // Allow time for reading from memory
  dut.clock.step(5)

  // Check the expected result if flag is true
  if (checkOutputCorrectness) {
    val expectedResult = leftTestVector.intersect(rightTestVector).sorted.take(vectorLength)
    for (i <- expectedResult.indices) {
      dut.io.readData(i).expect(expectedResult(i).U)
    }
  }
}


class TestVectorSkipAheadIntersectionUnitRegistered extends AnyFlatSpec with ChiselScalatestTester with Matchers {
  behavior of "VectorSkipAheadIntersectionUnitRegistered"

  val chiselTestDir = sys.env.getOrElse("CHISEL_TEST_DIR", "src/test/scala/saftool") // Default path if the environment variable is not set
  var verilog_dir = "src/verilog/"

  val numTagsValues = List(1,2,4) // 2, 4, 8, 16, 3
  val fiberLengths = List(8,16,32) // 2, 4, 8, 16, 32
  val vectorLengths = List(1,2,3,4) // 1,2,3,4,5,6,7,8

  val combinations = for {
    vectorLength <- vectorLengths
    numTags <- numTagsValues
    fiberLength <- fiberLengths
    if vectorLength <= 2*numTags && numTags <= fiberLength && vectorLength <= fiberLength
  } yield (vectorLength, numTags, log2Ceil(fiberLength))

  def createTest(vectorLength: Int, numTags: Int, tagBitWidth: Int): Unit = {
    val testName = s"test_VectorSkipAheadIntersectionUnitRegistered_vectorLength${vectorLength}_numTags${numTags}_tagBitWidth${tagBitWidth}.scala"
    val testFilePath = Paths.get(chiselTestDir, testName)

    if (!Files.exists(testFilePath)) {
      Files.createFile(testFilePath)
    }

    it should s"vectorLength${vectorLength}_numTags${numTags}_tagBitWidth${tagBitWidth}" in {
      test(new VectorSkipAheadIntersectionUnitRegistered(vectorLength, numTags, tagBitWidth))
        .withAnnotations(Seq(WriteVcdAnnotation))
        .runPeekPoke(new Workload_VectorSkipAheadIntersectionUnitRegistered(_))
    }
    emitVerilog(vectorLength, numTags, tagBitWidth)
  }

  def emitVerilog(vectorLength: Int, numTags: Int, tagBitWidth: Int): Unit = {
    val filename = s"VectorSkipAheadIntersectionUnitRegistered_vectorLength${vectorLength}_numTags${numTags}_tagBitWidth${tagBitWidth}.v"
    val verilogString = chisel3.getVerilogString(new VectorSkipAheadIntersectionUnitRegistered(vectorLength, numTags, tagBitWidth))
    Files.write(Paths.get(verilog_dir + filename), verilogString.getBytes(StandardCharsets.UTF_8))
  }

  combinations.foreach { case (vectorLength, numTags, tagBitWidth) =>
    createTest(vectorLength, numTags, tagBitWidth)
  }
}
