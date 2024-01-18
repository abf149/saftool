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

class Workload_VectorTwoFingerMergeIntersectionRegistered(dut: VectorTwoFingerMergeIntersectionRegistered) extends PeekPokeTester(dut) {

  val rand = new Random

  val numTags = dut.arraySize
  val vectorLength = numTags
  val maxTagValue = (1 << dut.metaDataWidth) - 1
  val checkOutputCorrectness = false

  def generateUniqueRandomList(size: Int, maxValue: Int): Seq[Int] = {
    val set = mutable.Set[Int]()
    while (set.size < size) {
      set += rand.nextInt(maxValue)
    }
    set.toSeq.sorted
  }

  val leftTestVector = generateUniqueRandomList(numTags, maxTagValue)
  val rightTestVector = generateUniqueRandomList(numTags, maxTagValue)

  dut.io.enable_in.poke(true.B)
  
  for (i <- leftTestVector.indices) {
    dut.io.inputWireArrays(0)(i).poke(leftTestVector(i).U)
    dut.io.inputWireArrays(1)(i).poke(rightTestVector(i).U)
  }

  dut.clock.step(5) // Wait for input stabilization
  dut.clock.step(10) // Allow time for processing

  if (checkOutputCorrectness) {
    val expectedResult = leftTestVector.intersect(rightTestVector).sorted.take(vectorLength)
    for (i <- expectedResult.indices) {
      dut.io.outputWireArrays(i).expect(expectedResult(i).U)
    }
  }

  dut.clock.step(5) // Additional steps for output stabilization
}

class Test_VectorTwoFingerMergeIntersectionRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "VectorTwoFingerMergeIntersectionRegistered"

  val arraySizes = List(1,2,4)
  val fiberLengths = List(8,16,32)
  val stageCounts = List(1,2,3,4,5,6,7,8)
  val chiselTestDir = sys.env.getOrElse("CHISEL_TEST_DIR", "src/test/scala/saftool")
  var verilog_dir = "src/verilog/"

  val combinations = for {
    arraySize <- arraySizes
    fiberLength <- fiberLengths
    stageCount <- stageCounts
    if arraySize < fiberLength && stageCount <= 2*arraySize
  } yield (log2Ceil(fiberLength), arraySize)

  def createTest(metaDataWidth: Int, arraySize: Int, numStages: Int): Unit = {


    val testName = s"test_VectorTwoFingerMergeIntersectionRegistered_metaDataWidth${metaDataWidth}_arraySize${arraySize}_numStages${numStages}.scala"
    val testFilePath = Paths.get(chiselTestDir, testName)

    if (!Files.exists(testFilePath)) {
      Files.createFile(testFilePath)
    }

    it should s"metaDataWidth${metaDataWidth}_arraySize${arraySize}_numStages${numStages}" in {


      test(new VectorTwoFingerMergeIntersectionRegistered(metaDataWidth, arraySize, numStages))
        .withAnnotations(Seq(WriteVcdAnnotation))
        .runPeekPoke(new Workload_VectorTwoFingerMergeIntersectionRegistered(_))


    }
    emitVerilog(metaDataWidth, arraySize, numStages)
  }

  def emitVerilog(metaDataWidth: Int, arraySize: Int, numStages: Int): Unit = {
    val filename = s"VectorTwoFingerMergeIntersectionRegistered_metaDataWidth${metaDataWidth}_arraySize${arraySize}_numStages${numStages}.v"
    val verilogString = chisel3.getVerilogString(new VectorTwoFingerMergeIntersectionRegistered(metaDataWidth, arraySize, numStages))
    Files.write(Paths.get(verilog_dir + filename), verilogString.getBytes(StandardCharsets.UTF_8))
  }

  combinations.foreach { case (metaDataWidth, arraySize, numStages) =>
    createTest(metaDataWidth, arraySize, numStages)
  }
}
